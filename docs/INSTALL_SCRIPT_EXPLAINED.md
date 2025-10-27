# 📖 Como Funciona o Script install_jetson.sh

## 🎯 Visão Geral

O script `install_jetson.sh` automatiza todo o processo de instalação do BMO na NVIDIA Jetson Orin, incluindo:
- Verificação de dependências
- Instalação de pacotes
- Configuração de modelos locais
- Otimização de performance
- Configuração inicial

**Tempo total estimado:** 20-30 minutos (dependendo da conexão de internet)

---

## 📋 Estrutura do Script

### Linha 7: `set -e`
```bash
set -e
```
**O que faz:** Se qualquer comando falhar (retornar erro), o script **para imediatamente**.

**Por quê:** Evita que o script continue se algo der errado (ex: CUDA não encontrado).

---

### Linhas 9-36: Funções de Output Colorido

```bash
GREEN='\033[0;32m'
RED='\033[0;31m'
# ...

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}
```

**O que faz:** Define cores ANSI e funções helper para imprimir mensagens formatadas.

**Resultado:**
```
[✓] Sucesso        # Verde
[!] Aviso          # Amarelo
[✗] Erro           # Vermelho
[i] Informação     # Azul
```

---

## 🔍 Etapa por Etapa

### 1️⃣ Verificação de Plataforma (Linhas 38-47)

```bash
if [ ! -f /etc/nv_tegra_release ]; then
    print_error "Este script é para NVIDIA Jetson. Plataforma não detectada."
    exit 1
fi

JETSON_MODEL=$(cat /proc/device-tree/model)
```

**O que faz:**
1. Verifica se o arquivo `/etc/nv_tegra_release` existe (exclusivo da Jetson)
2. Se não existir → não é Jetson → **sai com erro**
3. Se existir → lê o modelo exato da Jetson (Orin NX, AGX, etc.)

**Saída esperada:**
```
[i] Verificando plataforma...
[✓] Plataforma detectada: NVIDIA Jetson Orin NX
```

**Por quê importante:** Evita executar o script em PCs comuns, onde pode dar problemas.

---

### 2️⃣ Verificação de CUDA (Linhas 49-58)

```bash
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    print_status "CUDA detectado: $CUDA_VERSION"
else
    print_error "CUDA não encontrado. Instale JetPack SDK primeiro."
    exit 1
fi
```

**O que faz:**
1. Verifica se o comando `nvcc` (CUDA compiler) existe
2. Se existe → extrai a versão do CUDA
3. Se não existe → **sai com erro** (CUDA é obrigatório para GPU)

**Saída esperada:**
```
[i] Verificando CUDA...
[✓] CUDA detectado: 11.4
```

**Como funciona a extração da versão:**
```bash
nvcc --version
# Output: "Cuda compilation tools, release 11.4, V11.4.315"

# Pipe para grep → pega linha com "release"
# awk '{print $6}' → pega 6º campo ("V11.4.315")
# cut -c2- → remove primeiro caractere ("V")
# Resultado: "11.4.315"
```

---

### 3️⃣ Verificação de PyTorch (Linhas 60-77)

```bash
python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null
if [ $? -eq 0 ]; then
    PYTORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
    print_status "PyTorch $PYTORCH_VERSION com CUDA detectado"
else
    print_warning "PyTorch não tem suporte CUDA ou não está instalado"
    read -p "Continuar mesmo assim? (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

**O que faz:**
1. Tenta importar PyTorch e verificar se CUDA está disponível
2. Se sucesso (`$? -eq 0`) → mostra versão do PyTorch
3. Se falha → avisa e **pergunta** se quer continuar
4. Se resposta não for "y" ou "Y" → **sai**

**Saída esperada (sucesso):**
```
[i] Verificando Python e PyTorch...
[✓] Python 3.8.10 detectado
[✓] PyTorch 2.1.0a0+41361538.nv23.06 com CUDA detectado
```

**Saída esperada (falha):**
```
[!] PyTorch não tem suporte CUDA ou não está instalado
[i] Instale PyTorch para Jetson: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
Continuar mesmo assim? (y/N): _
```

**Por quê não para automaticamente:** PyTorch pode ser instalado depois, mas é avisado.

---

### 4️⃣ Atualização do Sistema (Linhas 79-83)

```bash
sudo apt update > /dev/null 2>&1
```

**O que faz:**
- Atualiza lista de pacotes disponíveis
- `> /dev/null 2>&1` → não mostra output detalhado (só mostra resumo)

**Por quê:** Garante que os pacotes mais recentes estão disponíveis.

---

### 5️⃣ Instalação de Dependências (Linhas 85-99)

```bash
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
```

**O que cada pacote faz:**

| Pacote | Função |
|--------|--------|
| `python3-pip` | Gerenciador de pacotes Python |
| `python3-venv` | Criar ambientes virtuais |
| `portaudio19-dev` | Biblioteca de áudio (necessária para PyAudio) |
| `python3-pyaudio` | Bindings Python para PortAudio |
| `ffmpeg` | Conversão de áudio/vídeo |
| `git` | Controle de versão (se precisar atualizar) |
| `flac` | Codec de áudio lossless |
| `libsndfile1` | Leitura/escrita de arquivos de áudio |
| `alsa-utils` | Utilitários de áudio ALSA (arecord, aplay) |

**Flag `-y`:** Responde "sim" automaticamente para todas as perguntas.

**Tempo:** 2-5 minutos

---

### 6️⃣ Verificação de Diretório (Linhas 101-106)

```bash
if [ ! -f "app/BMO.py" ]; then
    print_error "Execute este script do diretório raiz do BMO-Project"
    print_info "cd ~/BMO-Project && bash install_jetson.sh"
    exit 1
fi
```

**O que faz:**
- Verifica se `app/BMO.py` existe no diretório atual
- Se não existir → não está no diretório correto → **sai com erro**

**Por quê:** O script precisa ser executado de `~/BMO-Project/`, não de dentro de subpastas.

---

### 7️⃣ Criação do Ambiente Virtual (Linhas 108-116)

```bash
if [ -d "venv" ]; then
    print_warning "Ambiente virtual já existe, pulando..."
else
    python3 -m venv venv
    print_status "Ambiente virtual criado"
fi
```

**O que faz:**
1. Verifica se pasta `venv/` já existe
2. Se existe → pula (não recria)
3. Se não existe → cria ambiente virtual novo

**Por quê usar ambiente virtual:**
- Isola dependências do BMO do sistema
- Evita conflitos com outros projetos Python
- Permite diferentes versões de pacotes

---

### 8️⃣ Instalação de Dependências Python (Linhas 118-131)

```bash
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1

# Instalar requirements ARM64
pip install -r requirements/ARM64.txt --no-cache-dir

# Instalar extras para modelos locais
pip install langchain-ollama faster-whisper --no-cache-dir
```

**O que faz:**
1. **Ativa o ambiente virtual** (`source venv/bin/activate`)
2. **Atualiza pip** para versão mais recente
3. **Instala requirements ARM64** (LangChain, PyTorch, Coqui TTS, etc.)
4. **Instala extras** para modelos locais:
   - `langchain-ollama` → integração Ollama com LangChain
   - `faster-whisper` → STT local otimizado

**Flag `--no-cache-dir`:** Não usa cache, economiza espaço em disco.

**Tempo:** 10-15 minutos (download de ~2GB)

---

### 9️⃣ Instalação do Ollama (Linhas 133-143)

```bash
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
    print_status "Ollama já instalado: $OLLAMA_VERSION"
else
    print_info "Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh > /dev/null 2>&1
    print_status "Ollama instalado"
fi
```

**O que faz:**
1. Verifica se comando `ollama` já existe
2. Se existe → mostra versão e pula
3. Se não existe → baixa e executa script oficial de instalação

**Como funciona a instalação:**
- `curl -fsSL` → baixa o script de instalação
- `| sh` → executa o script
- Script oficial instala binário em `/usr/local/bin/ollama`

**Tempo:** 1-2 minutos

---

### 🔟 Seleção de Modelo LLM (Linhas 145-179)

```bash
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
        ollama pull llama3.2:3b
        MODEL_NAME="llama3.2:3b"
        ;;
    2)
        ollama pull llama3.1:8b
        MODEL_NAME="llama3.1:8b"
        ;;
    # ...
esac
```

**O que faz:**
1. **Mostra menu** com opções de modelos
2. **Lê escolha** do usuário (padrão = 2)
3. **Baixa modelo** escolhido via `ollama pull`
4. **Salva nome** do modelo em `$MODEL_NAME` (usado depois)

**Como funciona o padrão:**
- `read -p "..." model_choice` → lê input
- `model_choice=${model_choice:-2}` → se vazio, usa "2"

**Tempo por modelo:**
- llama3.2:3b → 5-10 min (~2GB)
- llama3.1:8b → 10-15 min (~4.5GB)
- gemma2:9b → 15-20 min (~5.5GB)

---

### 1️⃣1️⃣ Download de Modelos OpenWakeWord (Linhas 181-185)

```bash
python config/setup_oww.py > /dev/null 2>&1
```

**O que faz:**
- Executa script Python que baixa modelos base do OpenWakeWord
- Modelos salvos em `~/.local/share/openwakeword/`

**Tamanho:** ~50MB

**Tempo:** 1-2 minutos

---

### 1️⃣2️⃣ Configuração de Arquivos (Linhas 187-213)

```bash
if [ ! -f "config/config.yaml" ]; then
    cp config.yaml.example config/config.yaml

    # Atualizar config.yaml para modo local com GPU
    sed -i 's/mode: "cloud"/mode: "local"/' config/config.yaml
    sed -i "s/model: \"llama3.1:8b\"/model: \"$MODEL_NAME\"/" config/config.yaml
    sed -i 's/device: "cpu"/device: "cuda"/' config/config.yaml
    sed -i 's/compute_type: "int8"/compute_type: "float16"/' config/config.yaml
    sed -i 's/engine: "google"/engine: "coqui"/' config/config.yaml

    print_status "config.yaml criado (modo local + GPU)"
else
    print_warning "config.yaml já existe, não sobrescrevendo"
fi
```

**O que faz:**

1. **Verifica se `config.yaml` já existe**
2. Se não existe:
   - Copia do template (`config.yaml.example`)
   - **Modifica com `sed`** para configuração otimizada Jetson:

**Modificações automáticas:**

| Linha | De | Para | Por quê |
|-------|-----|------|---------|
| LLM mode | `mode: "cloud"` | `mode: "local"` | Usar Ollama local |
| LLM model | `model: "llama3.1:8b"` | `model: "$MODEL_NAME"` | Modelo escolhido |
| STT device | `device: "cpu"` | `device: "cuda"` | Usar GPU |
| STT compute | `compute_type: "int8"` | `compute_type: "float16"` | Otimizado para GPU |
| TTS engine | `engine: "google"` | `engine: "coqui"` | XTTS local |

**Como funciona o `sed`:**
```bash
sed -i 's/ANTIGO/NOVO/' arquivo.yaml
# -i → edita arquivo in-place
# s/ → substituir
# ANTIGO → padrão a buscar
# NOVO → substituição
```

**Se já existir:** Não sobrescreve (preserva configurações customizadas).

---

### 1️⃣3️⃣ Otimização de Performance (Linhas 215-228)

```bash
if sudo nvpmodel -m 0 2>/dev/null; then
    print_status "Modo MAXN ativado"
fi

if sudo jetson_clocks 2>/dev/null; then
    print_status "Clocks maximizados"
fi
```

**O que faz:**

1. **`nvpmodel -m 0`**: Ativa modo MAXN (performance máxima)
   - Desativa throttling de CPU/GPU
   - Usa mais energia, mas melhor performance

2. **`jetson_clocks`**: Fixa clocks no máximo
   - Impede GPU/CPU de baixar frequência
   - Reduz latência

**Por quê `2>/dev/null`:** Suprime mensagens de erro se comando não existir.

**Efeito:**
- CPU/GPU sempre em clock máximo
- Latência mais consistente
- Maior consumo de energia (~5-10W a mais)

---

### 1️⃣4️⃣ Configuração de Swap (Linhas 230-250)

```bash
SWAP_SIZE=$(free -h | grep Swap | awk '{print $2}')
print_info "Swap atual: $SWAP_SIZE"

if [[ "$SWAP_SIZE" == "0B" ]] || [[ -z "$SWAP_SIZE" ]]; then
    print_warning "Sem swap configurado"
    read -p "Criar swap de 8GB? (recomendado) (Y/n): " create_swap
    create_swap=${create_swap:-Y}

    if [[ $create_swap =~ ^[Yy]$ ]]; then
        sudo fallocate -l 8G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        sudo sysctl vm.swappiness=10
        echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    fi
fi
```

**O que faz:**

1. **Verifica swap atual** com `free -h`
2. Se swap é 0 ou vazio:
   - Pergunta se quer criar 8GB de swap
   - Se sim:
     - `fallocate -l 8G /swapfile` → cria arquivo de 8GB
     - `chmod 600` → permissões corretas (só root)
     - `mkswap` → formata como swap
     - `swapon` → ativa swap
     - Adiciona em `/etc/fstab` → ativa no boot
     - `vm.swappiness=10` → usa RAM antes de swap

**Por quê 8GB de swap:**
- BMO em modo local usa ~10GB RAM no pico
- Jetson Orin NX 16GB: 16GB RAM + 8GB swap = 24GB total
- Margem de segurança para não dar out-of-memory

**O que é swappiness:**
- Controla quando sistema usa swap
- `0` = nunca usa swap (exceto emergência)
- `10` = prefere RAM, usa swap se necessário
- `60` = padrão Linux (usa swap mais agressivamente)
- `100` = usa swap muito agressivamente

---

### 1️⃣5️⃣ Resumo Final (Linhas 252-286)

```bash
print_info "Configuração instalada:"
echo "  • LLM: Ollama ($MODEL_NAME)"
echo "  • STT: faster-whisper (GPU)"
echo "  • TTS: Coqui XTTS (GPU)"
# ...

print_info "Próximos passos:"
echo "1. Editar configurações (opcional)"
echo "2. Gravar amostra de voz para XTTS"
echo "3. Iniciar BMO"
# ...
```

**O que faz:**
- Mostra resumo da configuração instalada
- Lista próximos passos para usuário
- Links para documentação

---

## 🔄 Fluxograma do Script

```
START
  │
  ├─► Verificar se é Jetson → Não → EXIT(erro)
  │                         → Sim ↓
  │
  ├─► Verificar CUDA → Não → EXIT(erro)
  │                  → Sim ↓
  │
  ├─► Verificar PyTorch+CUDA → Não → Perguntar continuar? → Não → EXIT
  │                          → Sim ↓                       → Sim ↓
  │
  ├─► Atualizar sistema (apt update)
  │
  ├─► Instalar dependências (apt install)
  │
  ├─► Verificar diretório → Errado → EXIT(erro)
  │                       → Certo ↓
  │
  ├─► Criar venv (se não existir)
  │
  ├─► Instalar dependências Python
  │
  ├─► Instalar Ollama (se não instalado)
  │
  ├─► Menu: Escolher modelo LLM
  │      ├─► 1: Baixar llama3.2:3b
  │      ├─► 2: Baixar llama3.1:8b (padrão)
  │      ├─► 3: Baixar gemma2:9b
  │      └─► 4: Pular
  │
  ├─► Baixar modelos OpenWakeWord
  │
  ├─► Configurar config.yaml (se não existir)
  │      └─► sed: Modificar para modo local + GPU
  │
  ├─► Configurar .env (se não existir)
  │
  ├─► Ativar modo MAXN (nvpmodel)
  │
  ├─► Fixar clocks (jetson_clocks)
  │
  ├─► Verificar swap → Sem swap → Perguntar criar? → Sim → Criar 8GB
  │                  → Com swap ↓                    → Não ↓
  │
  ├─► Mostrar resumo
  │
  └─► END (sucesso)
```

---

## ⏱️ Linha do Tempo da Instalação

| Etapa | Tempo Estimado | O Que Está Acontecendo |
|-------|---------------|------------------------|
| 1. Verificações | 5-10s | Checando CUDA, PyTorch, plataforma |
| 2. apt update | 30-60s | Atualizando lista de pacotes |
| 3. apt install | 2-5min | Instalando dependências do sistema |
| 4. venv | 10s | Criando ambiente virtual |
| 5. pip install | 10-15min | **Mais demorado** - baixando ~2GB |
| 6. Ollama install | 1-2min | Instalando Ollama |
| 7. Modelo LLM | 5-20min | **Depende do modelo** - download |
| 8. OpenWakeWord | 1-2min | Baixando modelos wake word |
| 9. Configuração | 5-10s | Criando config.yaml |
| 10. Performance | 5s | Ativando MAXN |
| 11. Swap | 30-60s | Criando swapfile (se necessário) |
| **TOTAL** | **20-40min** | Depende de internet e modelo escolhido |

---

## 🧪 Testando o Script

### Simular sem Executar

```bash
# Ver o que seria feito
bash -x install_jetson.sh  # Modo debug (mostra cada comando)
```

### Testar em Partes

```bash
# Só verificações
bash install_jetson.sh  # Ctrl+C após verificações

# Continuar de onde parou
# (script detecta o que já está instalado)
```

---

## 🐛 O Que Pode Dar Errado

### 1. "Este script é para NVIDIA Jetson"

**Causa:** Executado em PC comum, não em Jetson.

**Solução:** Execute apenas na Jetson Orin.

---

### 2. "CUDA não encontrado"

**Causa:** JetPack SDK não instalado.

**Solução:**
```bash
# Instalar JetPack 5.x ou 6.x
# Via NVIDIA SDK Manager ou flash da imagem
```

---

### 3. "PyTorch não tem suporte CUDA"

**Causa:** PyTorch instalado via pip comum (não para Jetson).

**Solução:**
```bash
# Baixar wheel oficial NVIDIA
# Ver: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
```

---

### 4. Pip install trava/demora muito

**Causa:** Instalando pacotes grandes (PyTorch, TTS).

**Solução:** Paciência, pode demorar 15-20 min. Monitore com:
```bash
# Em outro terminal
top  # Ver uso de CPU/RAM
```

---

### 5. "Não foi possível ativar modo MAXN"

**Causa:** Comando `nvpmodel` não disponível.

**Solução:** Não é crítico, continua funcionando (só performance não otimizada).

---

### 6. Ollama pull falha

**Causa:** Problema de rede ou espaço em disco.

**Solução:**
```bash
# Verificar espaço
df -h

# Baixar manualmente depois
ollama pull llama3.1:8b
```

---

## 💡 Customizações Possíveis

### Mudar Modelo Padrão

```bash
# Linha 153: Mudar padrão de 2 para outro
model_choice=${model_choice:-1}  # Agora padrão é llama3.2:3b
```

### Desabilitar Otimizações de Performance

```bash
# Comentar linhas 217-227
# if sudo nvpmodel -m 0 2>/dev/null; then
#     ...
# fi
```

### Mudar Tamanho do Swap

```bash
# Linha 240: Mudar de 8G para outro valor
sudo fallocate -l 16G /swapfile  # 16GB ao invés de 8GB
```

### Instalar Mais Modelos

```bash
# Adicionar após linha 178:
4)
    ollama pull codellama:7b
    MODEL_NAME="codellama:7b"
    ;;
```

---

## 📊 Resumo Técnico

| Aspecto | Detalhe |
|---------|---------|
| **Linguagem** | Bash Script |
| **Requisitos** | Jetson Orin, JetPack 5+, 30GB espaço livre |
| **Tempo** | 20-40 minutos |
| **Tamanho Download** | ~6-10GB (depende do modelo) |
| **Ações sudo** | apt install, nvpmodel, jetson_clocks, swap |
| **Idempotente** | ✅ Sim (detecta o que já existe) |
| **Interativo** | Sim (escolha de modelo, swap) |
| **Rollback** | Não (manual) |
| **Logs** | Output para terminal |

---

## ✅ Checklist Pós-Instalação

Após executar o script, verifique:

- [ ] `ollama --version` funciona
- [ ] `ollama list` mostra modelo baixado
- [ ] `config/config.yaml` existe e tem `mode: "local"`
- [ ] `venv/` foi criado
- [ ] `free -h` mostra 8GB de swap (se criado)
- [ ] `nvidia-smi` mostra GPU
- [ ] `nvpmodel -q` mostra modo MAXN ativo

---

## 🎯 Próximos Passos Após Script

```bash
# 1. Gravar amostra de voz
arecord -f cd -d 10 bmo_voice_sample.wav

# 2. Iniciar BMO
source venv/bin/activate
python app/BMO.py
```

---

**Documentação completa:** `docs/JETSON_ORIN_DEPLOYMENT.md`
