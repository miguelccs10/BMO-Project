# 🚀 Setup Rápido - Modelos Locais do BMO

## 📋 Índice
1. [Configuração Completa Local](#configuração-completa-local)
2. [Configuração Híbrida](#configuração-híbrida-recomendado)
3. [Configuração Cloud (Padrão)](#configuração-cloud-padrão)
4. [Troubleshooting](#troubleshooting)

---

## ⚙️ Configuração Completa Local

### 1. Instalar Ollama (LLM Local)

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo (escolha um)
ollama pull llama3.2:3b      # Leve (4GB RAM)
ollama pull llama3.1:8b      # Recomendado (8GB RAM)
ollama pull mistral:7b       # Alternativa (8GB RAM)
```

### 2. Instalar Dependências Python

```bash
source venv/bin/activate

# LLM local
pip install langchain-ollama

# STT local
pip install faster-whisper

# TTS local (escolha um)
pip install piper-tts        # Rápido, leve
# ou use Coqui (já instalado)
```

### 3. Instalar Piper (se escolher Piper TTS)

```bash
# Via pip
pip install piper-tts

# Baixar voz PT-BR
piper --download-voice pt_BR-faber-medium
```

### 4. Configurar `config/config.yaml`

```yaml
# LLM Configuration
llm:
  mode: "local"  # ← Modo local

  local:
    provider: "ollama"
    model: "llama3.1:8b"  # ← Seu modelo
    base_url: "http://localhost:11434"
    timeout: 120

# STT Configuration
stt:
  mode: "local"  # ← Modo local

  local:
    provider: "faster-whisper"
    model: "small"  # ← tiny, base, small, medium, large-v3
    device: "cpu"   # ← ou "cuda" se tiver GPU
    compute_type: "int8"
    language: "pt"
    beam_size: 5

# TTS Configuration
tts:
  engine: "piper"  # ← ou "coqui" se preferir

  piper:
    voice: "pt_BR-faber-medium"
    quality: "medium"
    length_scale: 1.0
```

### 5. Testar

```bash
python app/BMO.py
```

**Saída esperada:**
```
🧠 Inicializando LLM em modo 'local'...
   🖥️  Usando LLM local: llama3.1:8b (Ollama)
🎤 Inicializando STT em modo 'local'...
   ⏳ Carregando faster-whisper modelo 'small'...
   🖥️  faster-whisper 'small' carregado com sucesso.
🔊 Usando motor de voz (TTS): 'piper'
✅ Piper TTS configurado
```

---

## 🔀 Configuração Híbrida (Recomendado)

Usa modelos locais quando possível, mas faz fallback para cloud se falhar.

### config.yaml

```yaml
llm:
  mode: "hybrid"  # ← Tenta local, fallback cloud

stt:
  mode: "hybrid"  # ← Tenta local, fallback cloud

tts:
  engine: "piper"  # ← Local, rápido
```

**Vantagens:**
- ✅ Usa local quando funciona (privacidade, sem custo)
- ✅ Fallback automático para cloud se local falhar
- ✅ Melhor para desenvolvimento/testes

---

## ☁️ Configuração Cloud (Padrão)

Usa serviços externos (configuração atual do projeto).

### config.yaml

```yaml
llm:
  mode: "cloud"  # ← Modo cloud

stt:
  mode: "cloud"  # ← Modo cloud

tts:
  engine: "google"  # ← ou "coqui"
```

**Requer:**
- API Keys no `.env`:
  - `GROQ_API_KEY` (LLM + STT)
  - Google Cloud credentials (TTS, se usar Google)

---

## 🔧 Configurações Avançadas

### Otimizar para Raspberry Pi

```yaml
llm:
  mode: "hybrid"
  local:
    model: "llama3.2:3b"  # ← Modelo menor

stt:
  mode: "local"
  local:
    model: "tiny"  # ← Modelo mais rápido
    device: "cpu"

tts:
  engine: "piper"  # ← Mais rápido que Coqui
  piper:
    voice: "pt_BR-edresson-low"  # ← Voz leve
```

### Otimizar para Workstation com GPU

```yaml
llm:
  mode: "local"
  local:
    model: "gemma2:9b"  # ← Modelo grande

stt:
  mode: "local"
  local:
    model: "large-v3"  # ← Melhor qualidade
    device: "cuda"     # ← Usar GPU
    compute_type: "float16"

tts:
  engine: "coqui"  # ← Melhor qualidade (usa GPU)
```

### Modo Completamente Offline

```yaml
llm:
  mode: "local"  # ← Sem fallback

stt:
  mode: "local"  # ← Sem fallback

tts:
  engine: "piper"  # ← ou "coqui", ambos locais

# Desabilitar ferramentas que precisam de internet
tools:
  spotify:
    enabled: false
  google_calendar:
    enabled: false
  google_search:
    enabled: false
```

---

## 🐛 Troubleshooting

### LLM: "Failed to initialize local LLM"

**Causa:** Ollama não está rodando

**Solução:**
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não responder, iniciar Ollama
ollama serve

# Verificar se modelo está baixado
ollama list
```

---

### STT: "faster-whisper não instalado"

**Causa:** Pacote não instalado

**Solução:**
```bash
pip install faster-whisper
```

---

### TTS: "piper command not found"

**Causa:** Piper não instalado corretamente

**Solução:**
```bash
# Via pip
pip install piper-tts

# Ou instalar binário
# Linux x86_64
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo mv piper /usr/local/bin/
```

---

### "Ollama connection timeout"

**Causa:** Modelo grande demorando para carregar

**Solução:**
```yaml
llm:
  local:
    timeout: 300  # ← Aumentar timeout (segundos)
```

---

### STT muito lento

**Causa:** Modelo grande demais para o hardware

**Solução:**
```yaml
stt:
  local:
    model: "tiny"  # ← Usar modelo menor
    # ou
    model: "base"
```

---

### TTS sem áudio (Piper)

**Causa:** Voz não baixada

**Solução:**
```bash
# Listar vozes disponíveis
piper --list-voices

# Baixar voz
piper --download-voice pt_BR-faber-medium
```

---

## 📊 Comparação de Performance

### Hardware Testado: PC Desktop (Intel i5, 16GB RAM)

| Configuração | Latência Total | RAM Usada | Qualidade |
|--------------|---------------|-----------|-----------|
| **Cloud (Atual)** | ~2-4s | ~2GB | ⭐⭐⭐⭐⭐ |
| **Híbrida** | ~3-6s | ~6GB | ⭐⭐⭐⭐ |
| **Local (small/8B)** | ~4-8s | ~10GB | ⭐⭐⭐⭐ |
| **Local (tiny/3B)** | ~2-5s | ~6GB | ⭐⭐⭐ |

### Hardware Testado: Raspberry Pi 4 (8GB)

| Configuração | Latência Total | RAM Usada | Qualidade |
|--------------|---------------|-----------|-----------|
| **Cloud** | ~3-5s | ~1GB | ⭐⭐⭐⭐⭐ |
| **Híbrida** | ~5-8s | ~4GB | ⭐⭐⭐⭐ |
| **Local (tiny/3B)** | ~10-20s | ~5GB | ⭐⭐⭐ |

**Recomendação:** Raspberry Pi funciona melhor em modo **cloud** ou **híbrido**.

---

## 🔐 Privacidade e Dados

### Modo Cloud
- ❌ Dados de voz enviados para Groq (STT)
- ❌ Conversas enviadas para Groq (LLM)
- ❌ Texto enviado para Google (TTS, se usar)
- ✅ Rápido e leve

### Modo Local
- ✅ Dados de voz processados localmente
- ✅ Conversas processadas localmente
- ✅ TTS gerado localmente
- ✅ Zero dependência de internet
- ❌ Requer mais hardware

---

## 📖 Mais Informações

- **Documentação Completa:** `docs/LOCAL_MODELS.md`
- **Lista de Modelos Ollama:** https://ollama.com/library
- **Vozes Piper PT-BR:** https://github.com/rhasspy/piper/releases
- **faster-whisper Performance:** https://github.com/guillaumekln/faster-whisper

---

## 🎯 Qual Configuração Escolher?

### Use **Cloud** se:
- Você tem internet estável
- Quer a melhor latência
- Hardware limitado (Raspberry Pi, PC antigo)
- Não se preocupa com privacidade

### Use **Híbrida** se:
- Quer equilíbrio entre privacidade e confiabilidade
- Tem 8-16GB RAM
- Internet às vezes instável
- **← Recomendado para maioria dos usuários**

### Use **Local** se:
- Privacidade é prioridade
- Sem internet disponível
- Tem hardware potente (16GB+ RAM)
- Quer zero custos de API
