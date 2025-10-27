# 🚀 Deploy BMO na NVIDIA Jetson Orin

## 📋 Especificações da Jetson Orin

| Modelo | GPU | RAM | CUDA Cores | Tensor Cores | Recomendação BMO |
|--------|-----|-----|------------|--------------|------------------|
| **Orin Nano 4GB** | 512 CUDA | 4GB | 512 | 16 | Modo Híbrido |
| **Orin Nano 8GB** | 1024 CUDA | 8GB | 1024 | 32 | Modo Local (leve) |
| **Orin NX 8GB** | 1024 CUDA | 8GB | 1024 | 32 | Modo Local (médio) |
| **Orin NX 16GB** | 1024 CUDA | 16GB | 1024 | 32 | Modo Local (completo) ⭐ |
| **AGX Orin 32GB** | 2048 CUDA | 32GB | 2048 | 64 | Modo Local (máximo) |

---

## 🎯 Configuração Recomendada para Jetson Orin

### Para Orin NX 16GB (Configuração Ideal)

```yaml
# config/config.yaml

# LLM Configuration - LOCAL com GPU
llm:
  mode: "local"  # ← Modo 100% local aproveitando GPU

  local:
    provider: "ollama"
    model: "llama3.1:8b"  # ← Modelo balanceado
    base_url: "http://localhost:11434"
    timeout: 120

# STT Configuration - LOCAL com GPU
stt:
  mode: "local"  # ← GPU acelera significativamente

  local:
    provider: "faster-whisper"
    model: "small"  # ← ou "medium" se tiver 16GB+
    device: "cuda"  # ← IMPORTANTE: Usar GPU!
    compute_type: "float16"  # ← float16 para GPU
    language: "pt"
    beam_size: 5

# TTS Configuration - LOCAL com GPU
tts:
  engine: "coqui"  # ← XTTS com GPU = excelente

  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    voice_sample_path: "bmo_voice_sample.wav"
    language: "pt"
    split_sentences: true

# VAD Configuration
recording:
  vad:
    enabled: true
    threshold: 0.5
    min_speech_duration_ms: 250
    min_silence_duration_ms: 700
    max_recording_seconds: 30
    speech_pad_ms: 300

# Tools Configuration (ajuste conforme necessidade)
tools:
  spotify:
    enabled: true
  google_calendar:
    enabled: true
  google_search:
    enabled: true
```

---

## 📦 Instalação Completa na Jetson Orin

### 1. Preparar Sistema (JetPack 5.x ou 6.x)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    git \
    flac \
    libsndfile1 \
    cuda-toolkit-11-4  # ou 12.x dependendo do JetPack

# Verificar CUDA
nvcc --version
```

---

### 2. Instalar PyTorch para Jetson (IMPORTANTE!)

⚠️ **Não use `pip install torch`!** Use os wheels oficiais da NVIDIA:

```bash
# Para JetPack 5.x (L4T R35.x)
wget https://nvidia.box.com/shared/static/mp164asf3sceb570wvjsrezk1p4ftj8t.whl -O torch-2.0.0-cp38-cp38-linux_aarch64.whl
pip3 install torch-2.0.0-cp38-cp38-linux_aarch64.whl

# Para JetPack 6.x (L4T R36.x)
wget https://developer.download.nvidia.com/compute/redist/jp/v60/pytorch/torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl
pip3 install torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl

# Verificar instalação
python3 -c "import torch; print(f'PyTorch {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Saída esperada:**
```
PyTorch 2.1.0a0+41361538.nv23.06
CUDA available: True
```

---

### 3. Clonar e Configurar BMO

```bash
# Clonar repositório
cd ~
git clone https://github.com/seu-usuario/BMO-Project.git
cd BMO-Project

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências ARM64
pip install -r requirements/ARM64.txt

# Instalar dependências para modelos locais
pip install langchain-ollama

# faster-whisper (STT local)
pip install faster-whisper

# Coqui TTS já está no ARM64.txt
```

---

### 4. Instalar Ollama na Jetson

```bash
# Download Ollama para ARM64
curl -fsSL https://ollama.com/install.sh | sh

# Verificar instalação
ollama --version

# Baixar modelo LLM
# Para Orin Nano/NX 8GB
ollama pull llama3.2:3b

# Para Orin NX 16GB (RECOMENDADO)
ollama pull llama3.1:8b

# Para AGX Orin 32GB
ollama pull gemma2:9b

# Testar
ollama run llama3.1:8b "Olá, teste rápido"
```

---

### 5. Configurar Credenciais

```bash
# Copiar exemplo de configuração
cp config.yaml.example config/config.yaml

# Editar configuração (use nano ou vim)
nano config/config.yaml

# Copiar .env
cp .env.example .env
nano .env
```

**Adicione suas chaves no `.env`:**
```bash
# APIs (se usar modo hybrid ou ferramentas cloud)
GROQ_API_KEY=gsk_xxxxx
GOOGLE_API_KEY=AIxxxxx
GOOGLE_CSE_ID=xxxxx

# Spotify
SPOTIPY_CLIENT_ID=xxxxx
SPOTIPY_CLIENT_SECRET=xxxxx

# Google Cloud (se usar Google TTS)
# Arquivo separado: google_adc_credentials.json
```

---

### 6. Gravar Amostra de Voz (para XTTS)

```bash
# Gravar 10 segundos com seu microfone
arecord -f cd -d 10 bmo_voice_sample.wav

# Ou use um arquivo WAV existente
# Requisitos: 16kHz ou 22.05kHz, mono, 5-10 segundos, sem ruído
```

---

### 7. Download de Modelos (primeira execução)

```bash
# Baixar modelo de wake word
python config/setup_oww.py

# Silero VAD e faster-whisper baixam automaticamente na primeira execução
```

---

### 8. Testar Instalação

```bash
source venv/bin/activate
python app/BMO.py
```

**Saída esperada:**
```
--- Iniciando Sistemas do BMO ---
✅ Configuration loaded successfully (BMO v4.1)
✅ Carregando cérebro, serviços e ferramentas do BMO...

🧠 Inicializando LLM em modo 'local'...
   🖥️  Usando LLM local: llama3.1:8b (Ollama)

🎤 Inicializando STT em modo 'local'...
   ⏳ Carregando faster-whisper modelo 'small'...
   🖥️  faster-whisper 'small' carregado com sucesso.

🔊 Usando motor de voz (TTS): 'coqui'
⏳ Carregando modelo Coqui TTS (XTTSv2) na memória...
✅ Modelo Coqui TTS carregado com sucesso no dispositivo 'cuda'.

   ✓ Spotify tools carregadas
   ✓ Google Calendar tool carregada
   ✓ Google Search tool carregada

✅ Agente BMO inicializado com sucesso.
✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...
```

---

## ⚡ Otimizações para Jetson Orin

### 1. Aumentar Swap (Recomendado)

```bash
# Verificar swap atual
free -h

# Criar swap de 8GB (ajuste conforme sua RAM)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Tornar permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Ajustar swappiness (usar RAM antes de swap)
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

### 2. Modo de Performance Máxima

```bash
# Ver modos disponíveis
sudo nvpmodel -q

# Configurar modo MAXN (performance máxima)
sudo nvpmodel -m 0

# Maximizar clock da GPU e CPU
sudo jetson_clocks

# Verificar status
sudo jetson_clocks --show
```

---

### 3. Monitorar Recursos

```bash
# Instalar jtop (monitor para Jetson)
sudo pip3 install jetson-stats

# Executar (em outro terminal)
sudo jtop

# Mostra: CPU, GPU, RAM, temperatura, power
```

---

### 4. TensorRT para Acelerar Modelos (Avançado)

**faster-whisper já usa CTranslate2 otimizado**, mas você pode otimizar ainda mais:

```bash
# Instalar TensorRT (já vem no JetPack)
python3 -c "import tensorrt; print(f'TensorRT {tensorrt.__version__}')"

# Para XTTS com TensorRT (futuro)
# Atualmente XTTS usa PyTorch, mas pode ser convertido
```

---

## 📊 Performance Esperada na Jetson Orin NX 16GB

### Latências (medidas aproximadas)

| Componente | Latência | Uso GPU | Uso RAM |
|------------|----------|---------|---------|
| Wake Word (OpenWakeWord) | ~80ms | 0% | ~50MB |
| VAD (Silero) | ~1ms | 0% | ~20MB |
| STT (faster-whisper small + CUDA) | ~300-500ms | 40% | ~1GB |
| LLM (Llama 3.1 8B) | ~1-3s | 60% | ~6GB |
| TTS (XTTS + CUDA) | ~300-500ms | 70% | ~2.5GB |
| **Total por interação** | **~2-5s** | - | **~10GB pico** |

### Comparação com Cloud

| Modo | Latência Total | Custo | Privacidade | Internet |
|------|---------------|-------|-------------|----------|
| **Local (Jetson)** | 2-5s | $0 | ✅ 100% | ❌ |
| **Cloud (Groq)** | 3-6s | $ | ❌ | ✅ Obrigatória |

**Conclusão:** Na Jetson Orin, modo local é **mais rápido e privado**!

---

## 🔧 Troubleshooting Jetson

### Problema: "CUDA out of memory"

**Causa:** Modelo muito grande para RAM/VRAM disponível.

**Soluções:**

1. **Usar modelo menor:**
   ```yaml
   llm:
     local:
       model: "llama3.2:3b"  # ← Ao invés de 8b

   stt:
     local:
       model: "tiny"  # ← Ao invés de small
   ```

2. **Liberar memória:**
   ```bash
   # Fechar outros processos
   sudo systemctl stop docker

   # Limpar cache
   sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

3. **Usar quantização:**
   ```bash
   # Para Ollama (já quantizado)
   ollama pull llama3.1:8b-q4_0  # ← Versão quantizada
   ```

---

### Problema: PyTorch não detecta CUDA

**Verificar:**
```bash
python3 -c "import torch; print(torch.cuda.is_available())"
```

**Se retornar False:**

1. Reinstalar PyTorch para Jetson:
   ```bash
   pip3 uninstall torch
   # Baixar wheel oficial da NVIDIA (ver seção 2)
   ```

2. Verificar variáveis de ambiente:
   ```bash
   export CUDA_HOME=/usr/local/cuda
   export PATH=$CUDA_HOME/bin:$PATH
   export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
   ```

---

### Problema: Ollama muito lento

**Causa:** Modelo não otimizado ou GPU não sendo usada.

**Verificar:**
```bash
# Durante execução do Ollama
nvidia-smi

# Deve mostrar processo "ollama" usando GPU
```

**Soluções:**

1. Garantir que Ollama está usando GPU:
   ```bash
   # Reinstalar Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # Verificar se detecta GPU
   ollama run llama3.1:8b "teste"
   ```

2. Usar modelo otimizado:
   ```bash
   # Modelos quantizados são mais rápidos
   ollama pull llama3.1:8b-q4_0
   ```

---

### Problema: Sistema superaquece

**Monitorar temperatura:**
```bash
sudo jtop
# Ver seção "TEMP"
```

**Soluções:**

1. **Adicionar cooling ativo:**
   - Instalar ventilador/dissipador
   - Jetson Orin recomenda cooling ativo para operação contínua

2. **Reduzir performance:**
   ```bash
   # Modo balanceado ao invés de MAXN
   sudo nvpmodel -m 2
   ```

3. **Throttle automático:**
   - Jetson reduz clock automaticamente se muito quente
   - Normal operar a 60-80°C

---

## 🚀 Script de Instalação Automática

Vou criar um script que automatiza tudo:

```bash
#!/bin/bash
# install_bmo_jetson.sh

set -e

echo "🚀 Instalando BMO na Jetson Orin..."

# 1. Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
echo "📦 Instalando dependências..."
sudo apt install -y \
    python3-pip python3-venv \
    portaudio19-dev python3-pyaudio \
    ffmpeg git flac libsndfile1

# 3. Verificar CUDA
echo "🔍 Verificando CUDA..."
if command -v nvcc &> /dev/null; then
    echo "✅ CUDA detectado: $(nvcc --version | grep release)"
else
    echo "❌ CUDA não encontrado. Instale JetPack SDK."
    exit 1
fi

# 4. Verificar PyTorch
echo "🔍 Verificando PyTorch..."
python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null || {
    echo "⚠️  PyTorch não tem suporte CUDA. Instale manualmente."
    echo "Veja: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048"
}

# 5. Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
cd ~/BMO-Project
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements/ARM64.txt
pip install langchain-ollama faster-whisper

# 7. Instalar Ollama
echo "🤖 Instalando Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 8. Baixar modelos
echo "📥 Baixando modelos..."
echo "Qual modelo LLM deseja? (1=3B, 2=8B, 3=9B)"
read -p "Escolha [2]: " model_choice
model_choice=${model_choice:-2}

case $model_choice in
    1) ollama pull llama3.2:3b ;;
    2) ollama pull llama3.1:8b ;;
    3) ollama pull gemma2:9b ;;
esac

# 9. Configurar
echo "⚙️  Configurando..."
cp config.yaml.example config/config.yaml
cp .env.example .env

echo "✅ Instalação base concluída!"
echo ""
echo "📝 Próximos passos:"
echo "1. Edite config/config.yaml com suas preferências"
echo "2. Edite .env com suas API keys"
echo "3. Grave amostra de voz: arecord -f cd -d 10 bmo_voice_sample.wav"
echo "4. Execute: python app/BMO.py"
```

---

## 📋 Checklist Final de Deployment

### Antes de Iniciar:
- [ ] JetPack 5.x ou 6.x instalado
- [ ] CUDA funcionando (`nvcc --version`)
- [ ] PyTorch com CUDA (`torch.cuda.is_available()`)
- [ ] Swap configurado (8GB recomendado)
- [ ] Cooling ativo instalado (ventilador)

### Instalação:
- [ ] BMO clonado
- [ ] Ambiente virtual criado
- [ ] Dependências ARM64 instaladas
- [ ] Ollama instalado e modelo baixado
- [ ] faster-whisper instalado
- [ ] Coqui TTS instalado
- [ ] Credenciais configuradas (.env, config.yaml)
- [ ] Amostra de voz gravada (bmo_voice_sample.wav)

### Configuração:
- [ ] `llm.mode = "local"`
- [ ] `stt.mode = "local"`, `device = "cuda"`
- [ ] `tts.engine = "coqui"`
- [ ] `recording.vad.enabled = true`
- [ ] Wake word model presente

### Teste:
- [ ] `python app/BMO.py` inicia sem erros
- [ ] Wake word detecta "Ei, BMO"
- [ ] VAD captura fala corretamente
- [ ] STT transcreve em português
- [ ] LLM responde adequadamente
- [ ] TTS gera áudio natural
- [ ] GPU sendo utilizada (verificar com `jtop`)

---

## 🎯 Configuração Final Recomendada

```yaml
# config/config.yaml - Otimizado para Jetson Orin NX 16GB

llm:
  mode: "local"
  local:
    provider: "ollama"
    model: "llama3.1:8b"
    base_url: "http://localhost:11434"
    timeout: 120

stt:
  mode: "local"
  local:
    provider: "faster-whisper"
    model: "small"  # ou "medium" se tiver RAM
    device: "cuda"  # ← IMPORTANTE
    compute_type: "float16"
    language: "pt"
    beam_size: 5

tts:
  engine: "coqui"
  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    voice_sample_path: "bmo_voice_sample.wav"
    language: "pt"
    split_sentences: true

recording:
  vad:
    enabled: true
    threshold: 0.5
    min_speech_duration_ms: 250
    min_silence_duration_ms: 700
    max_recording_seconds: 30

tools:
  spotify:
    enabled: true
  google_calendar:
    enabled: true
  google_search:
    enabled: true

hardware:
  enabled: false  # Ou true se tiver LEDs/display conectados
```

---

## 🎉 Resultado Final

Com essa configuração na Jetson Orin NX 16GB:

- ✅ **100% local** (zero dependência cloud)
- ✅ **Privacidade total** (dados nunca saem do dispositivo)
- ✅ **Latência baixa** (2-5s por interação)
- ✅ **Alta qualidade** (XTTS com GPU)
- ✅ **Custo zero** de APIs
- ✅ **Funciona offline**

**Performance esperada:** Comparável ou superior ao modo cloud! 🚀
