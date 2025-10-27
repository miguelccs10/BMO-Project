# 🏗️ Flexibilidade da Arquitetura do BMO

## 📊 Status Atual

| Componente | Providers Implementados | Facilidade de Adicionar Novos | Arquitetura |
|------------|------------------------|--------------------------------|-------------|
| **LLM** | Groq (cloud), Ollama (local) | ⭐⭐⭐⭐⭐ Muito fácil | Extensível |
| **STT** | Groq (cloud), faster-whisper (local) | ⭐⭐⭐⭐ Fácil | Extensível |
| **TTS** | Google, Coqui/XTTS, Piper, (ElevenLabs stub) | ⭐⭐⭐⭐ Fácil | Extensível |
| **Wake Word** | OpenWakeWord | ⭐⭐⭐ Moderado | Fixo (por ora) |
| **VAD** | Silero-VAD | ⭐⭐⭐ Moderado | Fixo (por ora) |

---

## ✅ O que É Flexível

### 1. LLM - Muito Flexível

Você pode **facilmente adicionar** novos providers:

**Exemplo: Adicionar OpenAI GPT-4**

```python
# bmo_core/agent/agent_executor.py

def _create_local_llm(self, temperature: float):
    """Create local LLM."""
    llm_config = self.config.config.llm.local
    provider = llm_config.provider.lower()

    if provider == "ollama":
        return ChatOllama(...)

    elif provider == "llamacpp":  # ← Novo provider
        from langchain_community.llms import LlamaCpp
        return LlamaCpp(
            model_path=llm_config.model_path,
            temperature=temperature,
            max_tokens=llm_config.max_tokens
        )

    elif provider == "openai":  # ← Outro novo
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=llm_config.model,
            temperature=temperature,
            api_key=self.config.get_api_key("openai")
        )
```

**config.yaml:**
```yaml
llm:
  mode: "local"
  local:
    provider: "llamacpp"  # ← ou "openai", "anthropic", etc
    model_path: "/path/to/model.gguf"
```

**Padrão de implementação:**
1. Adicione a condição no método `_create_local_llm()` ou `_create_cloud_llm()`
2. Importe a biblioteca necessária
3. Configure no YAML
4. Pronto!

---

### 2. STT - Flexível

**Exemplo: Adicionar Whisper.cpp (mais rápido que faster-whisper)**

```python
# bmo_core/services/audio_manager.py

def _transcribe_local(self, audio_file_path: str) -> Optional[str]:
    """Transcribe using local STT."""
    local_config = self.config.config.stt.local
    provider = local_config.provider.lower()

    if provider == "faster-whisper":
        # Implementação existente...

    elif provider == "whisper-cpp":  # ← Novo
        import whisper_cpp
        model = whisper_cpp.Whisper(model=local_config.model)
        result = model.transcribe(audio_file_path)
        return result['text']

    elif provider == "vosk":  # ← Outro novo (offline, leve)
        from vosk import Model, KaldiRecognizer
        model = Model(local_config.model_path)
        # ... implementação
```

**config.yaml:**
```yaml
stt:
  mode: "local"
  local:
    provider: "whisper-cpp"  # ← ou "vosk", "speechbrain", etc
```

---

### 3. TTS - Muito Flexível

**Já suporta 4 engines**, fácil adicionar mais:

**Exemplo: Adicionar Bark (TTS com emoções)**

```python
# bmo_core/services/audio_manager.py

def _init_tts(self):
    """Initialize TTS engine."""
    engine = self.tts_engine.lower()

    if engine == "google":
        self._init_google_tts()
    elif engine == "coqui":
        self._init_coqui_tts()
    elif engine == "piper":
        self._init_piper_tts()
    elif engine == "bark":  # ← Novo
        self._init_bark_tts()
    elif engine == "elevenlabs":
        self._init_elevenlabs_tts()

def _init_bark_tts(self):
    """Initialize Bark TTS."""
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models
        preload_models()
        self.bark_loaded = True
        print("✅ Bark TTS carregado.")
    except Exception as e:
        print(f"❌ Erro ao carregar Bark: {e}")
        self.tts_engine = None

def _tts_bark(self, text: str) -> Optional[str]:
    """Generate speech with Bark."""
    from bark import generate_audio, SAMPLE_RATE
    from scipy.io.wavfile import write

    audio_array = generate_audio(text, history_prompt="v2/pt_speaker_1")
    output_path = str(self.config.get_path('response_audio_wav'))
    write(output_path, SAMPLE_RATE, audio_array)
    return output_path
```

**config.yaml:**
```yaml
tts:
  engine: "bark"

  bark:
    voice_preset: "v2/pt_speaker_1"
    temperature: 0.7
```

---

## ❌ O que NÃO é Flexível (ainda)

### 1. Wake Word Detection

**Atualmente:** Fixo em OpenWakeWord com modelo ONNX.

**Para mudar:** Precisaria refatorar `app/BMO.py` e criar abstração.

**Dificuldade:** ⭐⭐⭐ Moderada

**Alternativas que poderiam ser implementadas:**
- Porcupine (Picovoice) - Mais preciso
- Snowboy - Descontinuado mas ainda usado
- Mycroft Precise - Open source
- PocketSphinx - Offline, leve

---

### 2. VAD (Voice Activity Detection)

**Atualmente:** Fixo em Silero-VAD.

**Para mudar:** Modificar `audio_manager.py:record_with_vad()`.

**Dificuldade:** ⭐⭐⭐ Moderada

**Alternativas:**
- WebRTC VAD - Mais leve, menos preciso
- PyAnnote - Mais preciso, mais pesado
- SpeechBrain VAD - Acadêmico, customizável

---

## 🔨 Como Adicionar um Novo Provider

### Exemplo Completo: Adicionar Claude (Anthropic) como LLM

#### 1. Instalar dependência
```bash
pip install langchain-anthropic
```

#### 2. Atualizar `config_manager.py`

```python
class LLMLocalConfig(BaseModel):
    """Local LLM configuration."""
    provider: str = Field(pattern="^(ollama|llamacpp|anthropic)$")  # ← Adicione
    model: str
    base_url: Optional[str] = None
    timeout: int = 120
```

#### 3. Atualizar `agent_executor.py`

```python
# No topo do arquivo
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# No método _create_local_llm
def _create_local_llm(self, temperature: float):
    llm_config = self.config.config.llm.local
    provider = llm_config.provider.lower()

    if provider == "ollama":
        # ... código existente

    elif provider == "anthropic":  # ← Novo
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("langchain-anthropic não instalado")

        print(f"   🤖 Usando LLM: Claude {llm_config.model} (Anthropic)")

        return ChatAnthropic(
            model=llm_config.model,
            temperature=temperature,
            anthropic_api_key=self.config.get_api_key("anthropic")
        )
```

#### 4. Atualizar `config_manager.py` (API keys)

```python
def get_api_key(self, service: str) -> Optional[str]:
    env_map = {
        "groq": "GROQ_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",  # ← Adicione
        # ...
    }
```

#### 5. Adicionar ao `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

#### 6. Configurar `config.yaml`

```yaml
llm:
  mode: "local"  # Ou "hybrid" se quiser fallback

  local:
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    timeout: 120
```

#### 7. Testar

```bash
python app/BMO.py
```

**Saída esperada:**
```
🧠 Inicializando LLM em modo 'local'...
   🤖 Usando LLM: Claude claude-3-5-sonnet-20241022 (Anthropic)
✅ Agente BMO inicializado com sucesso.
```

---

## 🎯 Facilidade de Adicionar Providers

### Muito Fácil (⭐⭐⭐⭐⭐)
- **LLM cloud providers** (OpenAI, Anthropic, Cohere, etc.)
  - LangChain já tem integrações prontas
  - Apenas adicionar condicionais e configuração

### Fácil (⭐⭐⭐⭐)
- **TTS engines** com API Python
- **STT engines** que retornam texto diretamente
- **LLM local** via LangChain Community

### Moderado (⭐⭐⭐)
- **Engines que usam subprocess** (como Piper atual)
- **Engines com setup complexo** (modelos grandes, dependências)
- **Wake Word detection alternativo**

### Difícil (⭐⭐)
- **Mudança de paradigma** (ex: streaming vs batch)
- **Engines com formato de I/O diferente**
- **Integração profunda com hardware**

---

## 📋 Checklist para Adicionar um Provider

### Para LLM:
- [ ] Instalar biblioteca (`pip install langchain-xyz`)
- [ ] Adicionar import com try/except
- [ ] Adicionar condição em `_create_local_llm()` ou `_create_cloud_llm()`
- [ ] Adicionar configuração no YAML (se necessário)
- [ ] Adicionar API key em `get_api_key()` (se necessário)
- [ ] Testar

### Para STT:
- [ ] Instalar biblioteca
- [ ] Adicionar em `_transcribe_local()` ou `_transcribe_cloud()`
- [ ] Configurar YAML
- [ ] Testar transcrição

### Para TTS:
- [ ] Instalar biblioteca
- [ ] Criar `_init_xyz_tts()`
- [ ] Criar `_tts_xyz()`
- [ ] Adicionar em `_init_tts()` e `text_to_speech_file()`
- [ ] Configurar YAML
- [ ] Testar síntese

---

## 🚀 Providers Sugeridos para Implementar

### LLM
- [ ] **LlamaCpp** - Modelos GGUF, muito rápido
- [ ] **OpenAI** - GPT-4, GPT-4o
- [ ] **Anthropic** - Claude 3.5
- [ ] **Google Gemini** - Via API
- [ ] **HuggingFace** - Inference API

### STT
- [ ] **Whisper.cpp** - Mais rápido que faster-whisper
- [ ] **Vosk** - Offline, multilíngue, leve
- [ ] **SpeechBrain** - Modelos customizáveis
- [ ] **Azure Speech** - Cloud enterprise

### TTS
- [ ] **Bark** - Emoções, múltiplas vozes
- [ ] **StyleTTS2** - Alta qualidade, rápido
- [ ] **ElevenLabs** - Cloud (já tem stub)
- [ ] **Azure TTS** - Cloud enterprise
- [ ] **MMS-TTS** (Meta) - 1100+ idiomas

---

## 💡 Dica: Modo Plugin

Se quiser **máxima flexibilidade**, poderia criar um sistema de plugins:

```python
# bmo_core/plugins/llm_plugins.py

class LLMPlugin(ABC):
    @abstractmethod
    def create_llm(self, config, temperature):
        pass

class OllamaPlugin(LLMPlugin):
    def create_llm(self, config, temperature):
        return ChatOllama(...)

class AnthropicPlugin(LLMPlugin):
    def create_llm(self, config, temperature):
        return ChatAnthropic(...)

# Registry
LLM_PLUGINS = {
    "ollama": OllamaPlugin(),
    "anthropic": AnthropicPlugin(),
}

# Uso
plugin = LLM_PLUGINS[provider]
llm = plugin.create_llm(config, temperature)
```

Isso permitiria **adicionar providers sem modificar código core**.

---

## ✅ Conclusão

### A arquitetura É flexível!

**Status atual:**
- ✅ Suporta múltiplos providers por componente
- ✅ Fácil adicionar novos (padrão claro)
- ✅ Configuração via YAML
- ✅ Fallback automático (hybrid mode)
- ✅ Lazy loading de modelos
- ⚠️ Limitado aos que já implementei (mas extensível)

**Para tornar MAIS flexível:**
- Sistema de plugins (futuro)
- Hot-reload de configuração (futuro)
- Auto-discovery de providers instalados (futuro)

**Mas hoje:** Você pode adicionar qualquer provider seguindo os exemplos deste documento! 🚀
