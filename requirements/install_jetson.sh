#!/bin/bash
# install_jetson.sh
# Script de instalação automática do BMO para NVIDIA Jetson Orin
# Autor: BMO Project
# Uso: bash install_jetson.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🤖 BMO - Instalação Jetson Orin 🤖    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Função para printar com cor
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# 1. Verificar se está rodando na Jetson
print_info "Verificando plataforma..."
if [ ! -f /etc/nv_tegra_release ]; then
    print_error "Este script é para NVIDIA Jetson. Plataforma não detectada."
    exit 1
fi

JETSON_MODEL=$(cat /proc/device-tree/model)
print_status "Plataforma detectada: $JETSON_MODEL"
echo ""

# 2. Verificar CUDA
print_info "Verificando CUDA..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    print_status "CUDA detectado: $CUDA_VERSION"
else
    print_error "CUDA não encontrado. Instale JetPack SDK primeiro."
    exit 1
fi
echo ""

# 3. Verificar Python e PyTorch
print_info "Verificando Python e PyTorch..."
PYTHON_VERSION=$(python3 --version)
print_status "$PYTHON_VERSION detectado"

python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null
if [ $? -eq 0 ]; then
    PYTORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
    print_status "PyTorch $PYTORCH_VERSION com CUDA detectado"
else
    print_warning "PyTorch não tem suporte CUDA ou não está instalado"
    print_info "Instale PyTorch para Jetson: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048"
    read -p "Continuar mesmo assim? (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 4. Atualizar sistema
print_info "Atualizando sistema (pode demorar)..."
sudo apt update > /dev/null 2>&1
print_status "Sistema atualizado"
echo ""

# 5. Instalar dependências do sistema
print_info "Instalando dependências do sistema..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    git \
    flac \
    libsndfile1 \
    alsa-utils > /dev/null 2>&1

print_status "Dependências instaladas"
echo ""

# 6. Verificar se já está no diretório BMO
if [ ! -f "app/BMO.py" ]; then
    print_error "Execute este script do diretório raiz do BMO-Project"
    print_info "cd ~/BMO-Project && bash install_jetson.sh"
    exit 1
fi

# 7. Criar ambiente virtual
print_info "Criando ambiente virtual Python..."
if [ -d "venv" ]; then
    print_warning "Ambiente virtual já existe, pulando..."
else
    python3 -m venv venv
    print_status "Ambiente virtual criado"
fi
echo ""

# 8. Ativar ambiente e instalar dependências
print_info "Instalando dependências Python (pode demorar 10-15 min)..."
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1

# Instalar requirements ARM64
pip install -r requirements/ARM64.txt --no-cache-dir

# Instalar extras para modelos locais
pip install langchain-ollama faster-whisper --no-cache-dir

print_status "Dependências Python instaladas"
echo ""

# 9. Instalar Ollama
print_info "Verificando Ollama..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
    print_status "Ollama já instalado: $OLLAMA_VERSION"
else
    print_info "Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh > /dev/null 2>&1
    print_status "Ollama instalado"
fi
echo ""

# 10. Perguntar qual modelo LLM baixar
print_info "Seleção de Modelo LLM:"
echo "  1) llama3.2:3b   (Leve, ~2GB RAM, rápido)"
echo "  2) llama3.1:8b   (Recomendado, ~6GB RAM, balanceado)"
echo "  3) gemma2:9b     (Pesado, ~8GB RAM, alta qualidade)"
echo "  4) Pular (baixar depois manualmente)"
echo ""
read -p "Escolha o modelo [2]: " model_choice
model_choice=${model_choice:-2}

case $model_choice in
    1)
        print_info "Baixando llama3.2:3b (pode demorar 5-10 min)..."
        ollama pull llama3.2:3b
        MODEL_NAME="llama3.2:3b"
        print_status "Modelo baixado"
        ;;
    2)
        print_info "Baixando llama3.1:8b (pode demorar 10-15 min)..."
        ollama pull llama3.1:8b
        MODEL_NAME="llama3.1:8b"
        print_status "Modelo baixado"
        ;;
    3)
        print_info "Baixando gemma2:9b (pode demorar 15-20 min)..."
        ollama pull gemma2:9b
        MODEL_NAME="gemma2:9b"
        print_status "Modelo baixado"
        ;;
    4)
        print_warning "Modelo não baixado. Execute manualmente: ollama pull llama3.1:8b"
        MODEL_NAME="llama3.1:8b"
        ;;
esac
echo ""

# 11. Baixar modelos OpenWakeWord
print_info "Baixando modelos OpenWakeWord..."
python config/setup_oww.py > /dev/null 2>&1
print_status "Modelos OpenWakeWord baixados"
echo ""

# 12. Configurar arquivos
print_info "Configurando arquivos..."

# Criar diretório de credenciais
if [ ! -d "credentials" ]; then
    mkdir -p credentials
    print_status "Diretório credentials/ criado"
else
    print_warning "Diretório credentials/ já existe"
fi

# Copiar config.yaml se não existir - usar versão otimizada do Jetson
if [ ! -f "config/config.yaml" ]; then
    if [ -f "config/config.jetson.yaml" ]; then
        cp config/config.jetson.yaml config/config.yaml
        # Atualizar modelo escolhido
        sed -i "s/model: \"llama3.1:8b\"/model: \"$MODEL_NAME\"/" config/config.yaml
        print_status "config.yaml criado (otimizado para Jetson + GPU)"
    else
        cp config.yaml.example config/config.yaml
        # Atualizar config.yaml para modo local com GPU
        sed -i 's/mode: "cloud"/mode: "local"/' config/config.yaml
        sed -i "s/model: \"llama3.1:8b\"/model: \"$MODEL_NAME\"/" config/config.yaml
        sed -i 's/device: "cpu"/device: "cuda"/' config/config.yaml
        sed -i 's/compute_type: "int8"/compute_type: "float16"/' config/config.yaml
        sed -i 's/engine: "google"/engine: "coqui"/' config/config.yaml
        print_status "config.yaml criado (modo local + GPU)"
    fi
else
    print_warning "config.yaml já existe, não sobrescrevendo"
fi

# Copiar .env se não existir
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status ".env criado"
else
    print_warning ".env já existe, não sobrescrevendo"
fi
echo ""

# 13. Configurar modo de performance
print_info "Otimizando performance da Jetson..."
if sudo nvpmodel -m 0 2>/dev/null; then
    print_status "Modo MAXN ativado"
else
    print_warning "Não foi possível ativar modo MAXN"
fi

if sudo jetson_clocks 2>/dev/null; then
    print_status "Clocks maximizados"
else
    print_warning "jetson_clocks não disponível"
fi
echo ""

# 14. Verificar swap
SWAP_SIZE=$(free -h | grep Swap | awk '{print $2}')
print_info "Swap atual: $SWAP_SIZE"
if [[ "$SWAP_SIZE" == "0B" ]] || [[ -z "$SWAP_SIZE" ]]; then
    print_warning "Sem swap configurado"
    read -p "Criar swap de 8GB? (recomendado) (Y/n): " create_swap
    create_swap=${create_swap:-Y}

    if [[ $create_swap =~ ^[Yy]$ ]]; then
        print_info "Criando swap de 8GB..."
        sudo fallocate -l 8G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile > /dev/null 2>&1
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
        sudo sysctl vm.swappiness=10
        echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf > /dev/null
        print_status "Swap de 8GB criado"
    fi
fi
echo ""

# 15. Resumo final
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Instalação Concluída! ✅        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
print_info "Configuração instalada:"
echo "  • LLM: Ollama ($MODEL_NAME)"
echo "  • STT: faster-whisper (GPU)"
echo "  • TTS: Coqui XTTS (GPU)"
echo "  • VAD: Silero-VAD"
echo "  • Wake Word: OpenWakeWord"
echo ""
print_info "Próximos passos:"
echo ""
echo "1. ${YELLOW}Configurar credenciais${NC} (se usar ferramentas cloud):"
echo "   • Google Calendar/Search: credentials/credentials.json"
echo "   • Google TTS: credentials/google_adc_credentials.json"
echo "   • Spotify: Editar .env (SPOTIPY_CLIENT_ID/SECRET)"
echo "   ${BLUE}Nota: Configuração atual usa modelos locais (não precisa credenciais)${NC}"
echo ""
echo "2. ${YELLOW}Editar configurações${NC} (opcional):"
echo "   nano config/config.yaml"
echo "   nano .env"
echo ""
echo "3. ${YELLOW}Gravar amostra de voz${NC} para XTTS (10 segundos):"
echo "   arecord -f cd -d 10 custom_models/bmo_voice_sample.wav"
echo "   (Fale uma frase completa com tom natural)"
echo ""
echo "4. ${YELLOW}Iniciar BMO${NC}:"
echo "   source venv/bin/activate"
echo "   python app/BMO.py"
echo ""
echo "5. ${YELLOW}Monitorar recursos${NC} (opcional):"
echo "   sudo pip3 install jetson-stats"
echo "   sudo jtop"
echo ""
print_status "Documentação completa: docs/JETSON_ORIN_DEPLOYMENT.md"
echo ""
print_info "Dica: Use 'Ctrl+C' para interromper o BMO"
echo ""
