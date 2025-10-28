#!/bin/bash
# install_desktop.sh
# Script de instalação automática do BMO para Desktop Linux (x86_64)
# Autor: BMO Project
# Uso: bash install_desktop.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🤖 BMO - Instalação Desktop 🤖      ║${NC}"
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

# 1. Detectar sistema operacional
print_info "Detectando sistema operacional..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
    print_status "Sistema detectado: $OS_NAME $OS_VERSION"
else
    print_warning "Não foi possível detectar o SO, assumindo Ubuntu/Debian"
    OS_NAME="Linux"
fi
echo ""

# 2. Verificar arquitetura
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    print_error "Este script é para x86_64. Arquitetura detectada: $ARCH"
    print_info "Use install_jetson.sh para ARM64/Jetson"
    exit 1
fi
print_status "Arquitetura: $ARCH"
echo ""

# 3. Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    print_error "Python 3.8+ requerido. Versão detectada: $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION detectado"
echo ""

# 4. Atualizar sistema
print_info "Atualizando lista de pacotes..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update > /dev/null 2>&1
    PKG_MANAGER="apt-get"
elif command -v dnf &> /dev/null; then
    sudo dnf check-update > /dev/null 2>&1 || true
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    sudo yum check-update > /dev/null 2>&1 || true
    PKG_MANAGER="yum"
elif command -v pacman &> /dev/null; then
    sudo pacman -Sy > /dev/null 2>&1
    PKG_MANAGER="pacman"
else
    print_error "Gerenciador de pacotes não suportado"
    print_info "Instale manualmente: python3-pip python3-venv portaudio19-dev ffmpeg git flac"
    exit 1
fi
print_status "Sistema atualizado"
echo ""

# 5. Instalar dependências do sistema
print_info "Instalando dependências do sistema..."

if [ "$PKG_MANAGER" == "apt-get" ]; then
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        portaudio19-dev \
        python3-pyaudio \
        ffmpeg \
        git \
        flac \
        libsndfile1 \
        alsa-utils > /dev/null 2>&1
elif [ "$PKG_MANAGER" == "dnf" ] || [ "$PKG_MANAGER" == "yum" ]; then
    sudo $PKG_MANAGER install -y \
        python3-pip \
        python3-virtualenv \
        portaudio-devel \
        python3-pyaudio \
        ffmpeg \
        git \
        flac \
        libsndfile \
        alsa-utils > /dev/null 2>&1
elif [ "$PKG_MANAGER" == "pacman" ]; then
    sudo pacman -S --noconfirm \
        python-pip \
        python-virtualenv \
        portaudio \
        python-pyaudio \
        ffmpeg \
        git \
        flac \
        libsndfile \
        alsa-utils > /dev/null 2>&1
fi

print_status "Dependências instaladas"
echo ""

# 6. Verificar se já está no diretório BMO
if [ ! -f "app/BMO.py" ]; then
    print_error "Execute este script do diretório raiz do BMO-Project"
    print_info "cd ~/BMO-Project && bash requirements/install_desktop.sh"
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
print_info "Instalando dependências Python (pode demorar 5-10 min)..."
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1

# Instalar requirements x86_64
pip install -r requirements/x86_64.txt --no-cache-dir

print_status "Dependências Python instaladas"
echo ""

# 9. Perguntar modo de operação
print_info "Escolha o modo de operação:"
echo "  1) Cloud (padrão) - Usa Groq API (requer chaves API)"
echo "  2) Local - Usa Ollama + modelos locais (privado, offline)"
echo "  3) Hybrid - Tenta local primeiro, fallback para cloud"
echo ""
read -p "Escolha o modo [1]: " mode_choice
mode_choice=${mode_choice:-1}

case $mode_choice in
    1)
        MODE="cloud"
        print_status "Modo selecionado: Cloud"
        NEED_OLLAMA=false
        ;;
    2)
        MODE="local"
        print_status "Modo selecionado: Local"
        NEED_OLLAMA=true
        ;;
    3)
        MODE="hybrid"
        print_status "Modo selecionado: Hybrid"
        NEED_OLLAMA=true
        ;;
    *)
        MODE="cloud"
        print_warning "Opção inválida, usando Cloud"
        NEED_OLLAMA=false
        ;;
esac
echo ""

# 10. Instalar Ollama se necessário
if [ "$NEED_OLLAMA" = true ]; then
    print_info "Verificando Ollama..."
    if command -v ollama &> /dev/null; then
        OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
        print_status "Ollama já instalado: $OLLAMA_VERSION"
    else
        print_info "Instalando Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh > /dev/null 2>&1
        print_status "Ollama instalado"
    fi

    # Perguntar qual modelo LLM baixar
    print_info "Seleção de Modelo LLM:"
    echo "  1) llama3.2:3b   (Leve, ~2GB RAM, rápido)"
    echo "  2) llama3.1:8b   (Recomendado, ~6GB RAM, balanceado)"
    echo "  3) llama3.1:70b  (Pesado, ~40GB RAM, alta qualidade)"
    echo "  4) Pular (baixar depois manualmente)"
    echo ""
    read -p "Escolha o modelo [2]: " model_choice
    model_choice=${model_choice:-2}

    case $model_choice in
        1)
            print_info "Baixando llama3.2:3b (pode demorar)..."
            ollama pull llama3.2:3b
            MODEL_NAME="llama3.2:3b"
            print_status "Modelo baixado"
            ;;
        2)
            print_info "Baixando llama3.1:8b (pode demorar)..."
            ollama pull llama3.1:8b
            MODEL_NAME="llama3.1:8b"
            print_status "Modelo baixado"
            ;;
        3)
            print_info "Baixando llama3.1:70b (pode demorar MUITO)..."
            ollama pull llama3.1:70b
            MODEL_NAME="llama3.1:70b"
            print_status "Modelo baixado"
            ;;
        4)
            print_warning "Modelo não baixado. Execute manualmente: ollama pull llama3.1:8b"
            MODEL_NAME="llama3.1:8b"
            ;;
    esac
    echo ""

    # Instalar modelos locais opcionais
    print_info "Instalando suporte para modelos locais..."
    pip install langchain-ollama faster-whisper piper-tts --no-cache-dir > /dev/null 2>&1
    print_status "Suporte local instalado"
    echo ""
fi

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

# Copiar config.yaml se não existir
if [ ! -f "config/config.yaml" ]; then
    cp config.yaml.example config/config.yaml

    # Ajustar configuração baseado no modo escolhido
    if [ "$MODE" == "local" ]; then
        sed -i 's/mode: "cloud"/mode: "local"/' config/config.yaml
        sed -i "s/model: \"llama3.1:8b\"/model: \"$MODEL_NAME\"/" config/config.yaml
        print_status "config.yaml criado (modo local)"
    elif [ "$MODE" == "hybrid" ]; then
        sed -i 's/mode: "cloud"/mode: "hybrid"/' config/config.yaml
        sed -i "s/model: \"llama3.1:8b\"/model: \"$MODEL_NAME\"/" config/config.yaml
        print_status "config.yaml criado (modo hybrid)"
    else
        print_status "config.yaml criado (modo cloud)"
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

# 13. Listar dispositivos de áudio
print_info "Listando dispositivos de áudio disponíveis..."
echo ""
python3 tutorials/list_audio_devices.py 2>/dev/null || print_warning "Não foi possível listar dispositivos de áudio"
echo ""

# 14. Resumo final
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ Instalação Concluída! ✅        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
print_info "Configuração instalada:"
if [ "$MODE" == "cloud" ]; then
    echo "  • Modo: Cloud (Groq API)"
    echo "  • LLM: Groq (llama-3.1-8b-instant)"
    echo "  • STT: Groq Whisper"
    echo "  • TTS: Google Cloud TTS"
else
    echo "  • Modo: $MODE"
    echo "  • LLM: Ollama ($MODEL_NAME)"
    echo "  • STT: Groq Whisper (cloud) + faster-whisper (local)"
    echo "  • TTS: Configurável (Google/Coqui/Piper)"
fi
echo "  • VAD: Silero-VAD"
echo "  • Wake Word: OpenWakeWord"
echo ""
print_info "Próximos passos:"
echo ""
echo "1. ${YELLOW}Configurar API keys${NC} no arquivo .env:"
echo "   nano .env"
if [ "$MODE" == "cloud" ]; then
    echo "   ${BLUE}[OBRIGATÓRIO] Configure:${NC}"
    echo "   • GROQ_API_KEY (para LLM e STT)"
    echo "   • SPOTIPY_CLIENT_ID/SECRET (para Spotify)"
    echo "   • GOOGLE_API_KEY, SEARCH_ENGINE_ID (para busca)"
else
    echo "   ${BLUE}[OPCIONAL] Configure se usar ferramentas cloud:${NC}"
    echo "   • GROQ_API_KEY (fallback STT/LLM em modo hybrid)"
    echo "   • SPOTIPY_CLIENT_ID/SECRET (para Spotify)"
fi
echo ""
echo "2. ${YELLOW}Configurar credenciais Google${NC} (se usar Calendar/TTS/Search):"
echo "   • credentials/credentials.json (Google Calendar OAuth)"
echo "   • credentials/google_adc_credentials.json (Google Cloud TTS/Search)"
echo "   ${BLUE}Ver README.md para instruções detalhadas${NC}"
echo ""
echo "3. ${YELLOW}Ajustar configurações${NC} (opcional):"
echo "   nano config/config.yaml"
echo "   • user_name: Seu nome"
echo "   • input_device_index: Índice do microfone (visto acima)"
echo "   • output_device_index: Índice do alto-falante"
echo ""
echo "4. ${YELLOW}Testar dispositivos de áudio${NC}:"
echo "   python tutorials/list_audio_devices.py"
echo ""
echo "5. ${YELLOW}Iniciar BMO${NC}:"
echo "   source venv/bin/activate"
echo "   python app/BMO.py"
echo ""
echo "   ${BLUE}Ou modo servidor (interface web):${NC}"
echo "   python app/bmo_server.py"
echo "   # Acesse: http://localhost:5000"
echo ""
print_status "Documentação completa: README.md e docs/"
echo ""
print_info "Dica: Use 'Ctrl+C' para interromper o BMO"
echo ""
