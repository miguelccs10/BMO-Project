# Guia de Modelos Locais para BMO

## 📋 Visão Geral dos Componentes

O BMO possui 5 componentes principais que usam modelos de IA:

| Componente | Status Atual | Opção Local Recomendada | Tamanho | Performance |
|------------|--------------|-------------------------|---------|-------------|
| **Wake Word** | ✅ Local (OpenWakeWord) | Talos.onnx | ~1.8MB | Excelente |
| **VAD** | ✅ Local (Silero-VAD) | silero_vad | ~1.8MB | Excelente |
| **LLM** | ☁️ Cloud (Groq) | Ollama | 2-8GB | Boa |
| **STT** | ☁️ Cloud (Groq/Whisper) | faster-whisper | 39MB-3GB | Excelente |
| **TTS** | 🔀 Misto (Google/Coqui) | Piper TTS | 10-50MB | Muito Boa |

---

## 🤖 LLM (Large Language Model)

### Opções de Deploy Local

#### **Ollama** (Recomendado)
- **Descrição**: Servidor local otimizado para rodar LLMs
- **Vantagens**:
  - Interface simples
  - Compatível com LangChain
  - Suporte a quantização (modelos menores)
  - Auto-gerenciamento de modelos
- **Instalação**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

#### **llama.cpp** (Alternativa)
- **Descrição**: Runtime C++ otimizado
- **Vantagens**: Menor uso de memória, mais rápido
- **Desvantagens**: Configuração mais complexa

### Modelos Recomendados

| Modelo | Parâmetros | RAM Mínima | Uso Recomendado | Qualidade |
|--------|-----------|------------|-----------------|-----------|
| **Llama 3.2 3B** | 3B | 4GB | Raspberry Pi, PC básico | ⭐⭐⭐ |
| **Llama 3.1 8B** | 8B | 8GB | PC desktop | ⭐⭐⭐⭐ |
| **Phi-3 Mini** | 3.8B | 4GB | Edge devices | ⭐⭐⭐ |
| **Mistral 7B** | 7B | 8GB | Conversação geral | ⭐⭐⭐⭐ |
| **Gemma 2 9B** | 9B | 10GB | Alta qualidade | ⭐⭐⭐⭐⭐ |

### Download via Ollama
```bash
# Modelos leves (3-4GB RAM)
ollama pull llama3.2:3b
ollama pull phi3:mini

# Modelos médios (8GB RAM)
ollama pull llama3.1:8b
ollama pull mistral:7b

# Modelos grandes (16GB+ RAM)
ollama pull gemma2:9b
```

---

## 🎤 STT (Speech-to-Text)

### faster-whisper (Recomendado)

**Descrição**: Reimplementação otimizada do Whisper usando CTranslate2
**Vantagens**:
- 4x mais rápido que whisper original
- Menor uso de memória
- Mesma qualidade
- Suporte a GPU e CPU

### Modelos Disponíveis

| Modelo | Tamanho | RAM | Velocidade | Qualidade | Uso Recomendado |
|--------|---------|-----|------------|-----------|-----------------|
| **tiny** | 39MB | 1GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Raspberry Pi |
| **base** | 74MB | 1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Edge devices |
| **small** | 244MB | 2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | PC básico |
| **medium** | 769MB | 5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | PC desktop |
| **large-v3** | 2.9GB | 10GB | ⚡ | ⭐⭐⭐⭐⭐ | Workstation |

### Instalação
```bash
pip install faster-whisper
```

### Performance Estimada (CPU Intel i5)
- **tiny**: ~5x tempo real (1s de áudio = 0.2s processamento)
- **base**: ~3x tempo real
- **small**: ~1.5x tempo real
- **medium**: ~0.8x tempo real (mais lento que tempo real)

---

## 🔊 TTS (Text-to-Speech)

### Opções Locais

#### **Coqui TTS XTTSv2** (Já implementado)
- **Qualidade**: ⭐⭐⭐⭐⭐ (Muito natural)
- **Velocidade**: Lento (~2-3s para frase curta)
- **Tamanho**: ~2GB
- **Vantagens**: Clonagem de voz, múltiplos idiomas
- **Desvantagens**: Requer GPU para ser prático

#### **Piper TTS** (Nova opção - Recomendado para CPU)
- **Qualidade**: ⭐⭐⭐⭐ (Natural)
- **Velocidade**: ⚡⚡⚡⚡ Muito rápido (~0.2s)
- **Tamanho**: 10-50MB por voz
- **Vantagens**: Extremamente rápido em CPU, múltiplas vozes PT-BR
- **Desvantagens**: Menos natural que Coqui

#### **Bark** (Alternativa)
- **Qualidade**: ⭐⭐⭐⭐⭐ (Muito natural, com emoções)
- **Velocidade**: Muito lento (~10-15s)
- **Uso**: Geração offline, não tempo real

### Vozes PT-BR para Piper

| Voz | Qualidade | Velocidade | Tamanho | Gênero |
|-----|-----------|------------|---------|--------|
| `pt_BR-faber-medium` | Alta | Média | 63MB | Masculino |
| `pt_BR-edresson-low` | Média | Rápida | 18MB | Masculino |

### Instalação Piper
```bash
pip install piper-tts
```

---

## 🎯 Configurações Recomendadas por Hardware

### **Raspberry Pi 4/5 (4-8GB RAM)**
```yaml
llm:
  mode: "local"
  local:
    provider: "ollama"
    model: "llama3.2:3b"
stt:
  mode: "local"
  local:
    model: "tiny"  # ou "base"
tts:
  engine: "piper"
```

### **PC Desktop (16GB RAM, sem GPU)**
```yaml
llm:
  mode: "local"
  local:
    provider: "ollama"
    model: "llama3.1:8b"
stt:
  mode: "local"
  local:
    model: "small"  # ou "medium"
tts:
  engine: "piper"
```

### **Workstation (32GB RAM, GPU)**
```yaml
llm:
  mode: "local"
  local:
    provider: "ollama"
    model: "gemma2:9b"
stt:
  mode: "local"
  local:
    model: "large-v3"
    device: "cuda"
tts:
  engine: "coqui"  # Já implementado
```

### **Modo Cloud (Atual)**
```yaml
llm:
  mode: "cloud"
  provider: "groq"
stt:
  mode: "cloud"
  provider: "groq"
tts:
  engine: "google"
```

---

## 📊 Comparação de Performance

### Latência Típica por Componente

| Componente | Cloud | Local (PC) | Local (RPi) |
|------------|-------|------------|-------------|
| Wake Word | ~80ms | ~80ms | ~80ms |
| VAD | ~1ms | ~1ms | ~1ms |
| STT | ~500-1000ms | ~300-800ms | ~1-3s |
| LLM | ~500-1500ms | ~1-5s | ~5-15s |
| TTS | ~1000-2000ms | ~200-500ms (Piper) | ~1-2s |
| **Total** | **2-5s** | **1.5-6.5s** | **7-20s** |

### Uso de Disco

| Configuração | Espaço Necessário |
|--------------|-------------------|
| Mínima (tiny/3B) | ~4GB |
| Recomendada (small/8B) | ~10GB |
| Alta (medium/9B) | ~15GB |
| Máxima (large/13B) | ~25GB |

---

## 🚀 Setup Rápido

### 1. Instalar Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

### 2. Instalar Dependências Python
```bash
pip install faster-whisper piper-tts langchain-ollama
```

### 3. Configurar BMO
Edite `config/config.yaml`:
```yaml
llm:
  mode: "local"  # Mude de "cloud" para "local"
  local:
    provider: "ollama"
    model: "llama3.1:8b"
    base_url: "http://localhost:11434"

stt:
  mode: "local"  # Mude de "cloud" para "local"
  local:
    provider: "faster-whisper"
    model: "small"
    device: "cpu"  # ou "cuda" se tiver GPU

tts:
  engine: "piper"  # Nova opção
  piper:
    voice: "pt_BR-faber-medium"
    quality: "medium"
```

### 4. Testar
```bash
python app/BMO.py
```

---

## 🔄 Modo Híbrido (Recomendado)

Configure fallback para usar cloud se local falhar:

```yaml
llm:
  mode: "hybrid"  # Tenta local, fallback para cloud

stt:
  mode: "hybrid"

# TTS não precisa de hybrid (já é local com Coqui/Piper)
```

---

## 📈 Próximos Passos

1. ✅ Wake Word Detection (Local)
2. ✅ VAD (Local)
3. 🔄 LLM Local (Ollama)
4. 🔄 STT Local (faster-whisper)
5. 🔄 TTS Local otimizado (Piper)
6. 🎯 Sistema de fallback cloud
7. 🎯 Cache de respostas
8. 🎯 Modo offline completo

---

## 📝 Notas de Segurança e Privacidade

**Vantagens de Modelos Locais:**
- ✅ Zero dependência de internet
- ✅ Dados nunca saem do dispositivo
- ✅ Sem custos de API
- ✅ Sem limites de rate
- ✅ Funciona offline

**Desvantagens:**
- ⚠️ Requer hardware mais potente
- ⚠️ Latência pode ser maior em hardware limitado
- ⚠️ Requer gerenciamento de modelos
- ⚠️ Atualizações manuais dos modelos
