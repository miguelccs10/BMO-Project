# BMO Project Codebase - Comprehensive Exploration Report

**Project**: BMO - AI Voice Assistant inspired by Adventure Time  
**Location**: /home/miguel/BMO-Project  
**Last Updated**: October 27, 2025  
**Git Status**: Main branch (clean)  

---

## 1. OVERALL PROJECT STRUCTURE

### Directory Tree

```
/home/miguel/BMO-Project/
├── app/                          # Entry points
│   ├── BMO.py                   # Standalone mode with wake-word detection
│   └── bmo_server.py            # Flask server with WebSocket support
│
├── bmo_core/                    # Core functionality
│   ├── agent/
│   │   ├── agent_executor.py    # LangChain agent with routing (238 lines)
│   │   └── memory.py            # Conversation memory management (30 lines)
│   │
│   ├── services/
│   │   ├── audio_manager.py     # STT/TTS engine abstraction (629 lines)
│   │   ├── hardware_manager.py  # GPIO/LED control (38 lines)
│   │   ├── display_manager.py   # OLED display abstraction (55 lines)
│   │   └── wake_word_detector.py # Legacy wake-word detector (58 lines)
│   │
│   ├── tools/
│   │   ├── spotify.py           # Spotify control (131 lines)
│   │   ├── calendar.py          # Google Calendar integration (67 lines)
│   │   ├── search.py            # Google Search wrapper (16 lines)
│   │   └── __init__.py          # Tools package
│   │
│   └── __init__.py
│
├── config/                      # Configuration system
│   ├── config_manager.py        # Pydantic-based config loader (469 lines)
│   ├── config.yaml              # Main configuration file
│   ├── config.jetson.yaml       # NVIDIA Jetson-optimized config
│   ├── prompts.yaml             # LLM prompts & templates
│   ├── settings.py              # Legacy compatibility wrapper
│   ├── prompts.py               # Legacy compatibility wrapper
│   └── setup_oww.py             # OpenWakeWord model downloader
│
├── custom_models/               # ML models
│   ├── wake_word/
│   │   ├── Talos.onnx           # Current wake-word model (205KB)
│   │   └── ei_bmo.onnx          # Alternative wake-word model (205KB)
│   ├── bmo_voice_sample.wav     # Voice cloning sample
│   └── record_samples.py        # Utility for recording voice samples
│
├── requirements/                # Dependencies
│   ├── x86_64.txt               # PC/desktop requirements
│   └── ARM64.txt                # Raspberry Pi/Jetson requirements
│
├── docs/                        # Comprehensive documentation (3,327 lines)
│   ├── JETSON_ORIN_DEPLOYMENT.md
│   ├── AUDIO_DEVICES.md
│   ├── LOCAL_MODELS.md
│   ├── LOCAL_SETUP_QUICK_START.md
│   ├── TTS_COMPARISON.md
│   ├── ARCHITECTURE_FLEXIBILITY.md
│   └── INSTALL_SCRIPT_EXPLAINED.md
│
├── tutorials/                   # Utility scripts
│   └── list_audio_devices.py    # Audio device enumeration
│
├── web/                         # Web interface
│   └── index.html               # Browser-based UI with WebSocket
│
├── config.yaml.example          # Configuration template
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── CLAUDE.md                    # This project's development guidelines
├── README.md                    # Main documentation
└── requirements/                # Python dependencies

Note: CROS_2025/ directory is not present - wake-word training pipeline mentioned in CLAUDE.md
```

---

## 2. CONFIGURATION ARCHITECTURE

### Configuration System (Advanced)

**Modern YAML + Pydantic Pattern**

The project uses a sophisticated, type-safe configuration system:

**ConfigManager (`config/config_manager.py`)**
- Singleton pattern: `get_config()` returns same instance across modules
- Loads from `config.yaml` and `prompts.yaml` at startup
- Full Pydantic validation with typed models
- Automatic environment variable management
- Path resolution (absolute/relative)
- API key management from `.env`

**Pydantic Models** (469 lines of type definitions):
```
BMOConfig (root)
├── ProjectConfig (name, version, user_name)
├── LLMConfig (mode: cloud/local/hybrid)
│   ├── LLMCloudConfig (Groq)
│   ├── LLMLocalConfig (Ollama)
│   ├── LLMTemperatures (router, agent, conversation)
│   └── AgentConfig (max_iterations, verbose, error_handling)
├── TTSConfig (engine: google/coqui/piper/elevenlabs)
│   ├── GoogleTTSConfig
│   ├── CoquiTTSConfig
│   ├── PiperTTSConfig
│   └── ElevenLabsTTSConfig
├── STTConfig (mode: cloud/local/hybrid)
│   ├── STTCloudConfig (Groq Whisper)
│   └── STTLocalConfig (faster-whisper)
├── WakeWordConfig (OpenWakeWord)
│   └── WakeWordAudioConfig
├── RecordingConfig
│   └── VADConfig (Voice Activity Detection settings)
├── ToolsConfig (enable/disable each tool)
├── SpotifyConfig
├── GoogleCalendarConfig
├── GoogleCloudConfig
├── ServerConfig (Flask)
├── LangChainConfig (LangSmith integration)
├── PathsConfig (file paths)
├── HardwareConfig
│   └── DisplayConfig
└── PromptsConfig (from prompts.yaml)
```

**Configuration Files**:

1. **config.yaml** (174 lines)
   - Main configuration for deployment
   - LLM: "cloud" mode (Groq) by default
   - TTS: Google Cloud by default
   - STT: Groq Whisper Cloud by default
   - Wake-word: Talos.onnx model
   - VAD enabled for intelligent silence detection

2. **config.jetson.yaml** (222 lines)
   - NVIDIA Jetson Orin optimized
   - LLM: "local" mode (Ollama with GPU)
   - TTS: Coqui XTTS (GPU accelerated)
   - STT: faster-whisper (GPU accelerated)
   - Detailed comments for Jetson deployment

3. **prompts.yaml** (55 lines)
   - BMO personality prompt (Portuguese)
   - Router template for intent classification
   - Error messages and response templates
   - Supports {user_name} template substitution

4. **config.yaml.example** (100 lines)
   - Template for users to copy and customize
   - Well-commented with options and explanations

5. **.env.example** (13 lines)
   - Template for API keys
   - Defines required environment variables

**Legacy Compatibility**:
- `config/settings.py` - Wraps ConfigManager for backward compatibility
- `config/prompts.py` - Provides old-style prompt access
- Both deprecated in favor of direct `get_config()` usage

**Configuration Usage Pattern**:
```python
from config.config_manager import get_config

config = get_config()
# Access config
model = config.config.llm.cloud.model_name
# Get API keys
groq_key = config.get_api_key("groq")
# Get resolved paths
wake_word_path = config.get_wake_word_model_path()
# Get formatted prompts
system_prompt = config.get_system_prompt()  # Auto-fills {user_name}
```

---

## 3. CORE ARCHITECTURE

### Entry Points

**1. BMO.py (Autonomous Mode)**
- Wake-word detection loop using OpenWakeWord
- Microphone-based audio input
- VAD-based automatic speech end detection
- Local playback of responses
- LED and OLED display feedback
- Persistent session ID for conversation memory
- Auto-detects Raspberry Pi vs. simulation mode

**2. bmo_server.py (Flask WebSocket Server)**
- HTTP REST interface (serves web UI)
- WebSocket endpoint for audio streaming
- WebM to WAV conversion
- Auto-reconnection logic
- Per-connection session management
- Suitable for browser-based interfaces

### Agent Architecture (LangChain)

**Three-Tier Routing System** (`bmo_core/agent/agent_executor.py` - 238 lines):

```
User Input
    ↓
┌─────────────────────────┐
│  ROUTER CHAIN           │
│  (ChatGroq temp=0)      │
│  Structured Output      │
│  Decision: "ferramentas"│
│          or "conversa"  │
└──────────┬──────────────┘
           │
    ┌──────┴──────┐
    ↓             ↓
┌────────────┐ ┌──────────────────┐
│ CONVERSA   │ │ FERRAMENTAS      │
│ CHAIN      │ │ AGENT CHAIN      │
│            │ │                  │
│ General    │ │ Tool Calling:    │
│ conversation│ │ • Spotify        │
│            │ │ • Calendar       │
│            │ │ • Search         │
└──────┬─────┘ └────────┬─────────┘
       │                │
       └────────┬───────┘
                ↓
        ┌───────────────┐
        │ Shared Memory │
        │ (ChatHistory) │
        └───────────────┘
                ↓
         User Response
```

**Components**:

1. **Router Chain**
   - LLM: ChatGroq with temperature=0
   - Structured output: `RouteQuery` model
   - Decision: "ferramentas" or "conversa"
   - Has access to full chat history

2. **Conversation Chain**
   - LLM: ChatGroq with configurable temperature
   - Prompt: System personality + chat history + input
   - Output parser: StrOutputParser

3. **Tool Agent Chain**
   - Agent: `create_openai_tools_agent`
   - Uses LangChain Hub prompt: `hwchase17/openai-tools-agent`
   - Executor: `AgentExecutor` (configurable max_iterations)
   - Tools: Conditionally loaded based on config

4. **Memory Management** (`bmo_core/agent/memory.py` - 30 lines)
   - In-memory session storage: `SESSION_HISTORIES` dict
   - `RunnableWithMessageHistory` wrapper
   - Session ID-based isolation
   - Input key: "input"
   - History key: "chat_history"
   - Output key: "output"

**Tool Integration**:
- Each tool decorated with `@tool`
- Conditional loading based on `config.yaml`
- Error handling with BMO personality response
- Three tools currently implemented (see Tools section below)

### Services Layer

**1. AudioManager** (`bmo_core/services/audio_manager.py` - 629 lines)

Multi-engine support for both STT and TTS:

**STT (Speech-to-Text)**:
- **Cloud Mode**: Groq Whisper API (fast, cloud-dependent)
- **Local Mode**: faster-whisper with ONNX (offline, CPU/GPU)
- **Hybrid Mode**: Try local first, fallback to cloud
- Configuration: Model size (tiny/base/small/medium/large-v3)
- Support for GPU acceleration (CUDA)

**TTS (Text-to-Speech)**:
- **Google Cloud TTS**: High-quality, cloud-dependent
  - Supports multiple voices and languages
  - Output formats: MP3, LINEAR16, OGG_OPUS
- **Coqui TTS (XTTSv2)**: Free, local, voice cloning
  - GPU accelerated if available
  - Speaker voice cloning from sample file
  - Multilingual support
- **Piper TTS**: Fast, lightweight, CPU-friendly
  - Runs via subprocess
  - Portuguese voices available
- **ElevenLabs**: Placeholder (not yet implemented)

**VAD (Voice Activity Detection)**:
- Silero VAD model (torch-based)
- Configurable thresholds and durations
- Automatic speech/silence detection
- Max recording duration safety limit
- Speech padding for natural recording

**Recording**:
- Fixed-duration recording (fallback)
- VAD-based adaptive recording
- Buffer clearing to prevent echo
- Configurable sample rate, chunk size
- Support for multiple audio devices

**2. HardwareManager** (`bmo_core/services/hardware_manager.py` - 38 lines)

- Auto-detects Raspberry Pi vs. PC
- GPIO control for LEDs (pin 17)
- Graceful degradation in simulation mode
- LED on/off functions
- Cleanup on exit

**3. DisplayManager** (`bmo_core/services/display_manager.py` - 55 lines)

- Auto-detects Raspberry Pi with OLED display
- SSD1306 OLED support via Adafruit library
- Face expressions: "neutral", "listening", "thinking", "speaking", "happy"
- Graceful degradation to console output

**4. WakeWordDetector** (`bmo_core/services/wake_word_detector.py` - 58 lines)

**Note**: This is LEGACY code using PicoVoice. Current system uses OpenWakeWord directly in BMO.py.
- Old implementation using Porcupine
- Superseded by OpenWakeWord integration in main BMO.py
- Should be considered for removal or update

### Tools Layer

**1. Spotify** (`bmo_core/tools/spotify.py` - 131 lines)

Three LangChain-decorated tools:
- `play_music_on_spotify(song_name, artist_name)`: Search and play
- `control_spotify_playback(action)`: pause/resume/next/previous
- `get_current_spotify_song()`: Get currently playing track

Features:
- Auto-detects active Spotify device
- Robust input sanitization (strips quotes from LLM output)
- Proper error handling with friendly messages
- Connection handling

**2. Calendar** (`bmo_core/tools/calendar.py` - 67 lines)

Single tool:
- `get_next_appointment()`: Fetches next event from Google Calendar

Features:
- OAuth flow for desktop apps
- Token refresh handling
- ISO 8601 datetime parsing
- Formatted Portuguese date output

**3. Search** (`bmo_core/tools/search.py` - 16 lines)

Single tool:
- `google_search_tool`: Wrapper around GoogleSearchAPIWrapper
- Uses `langchain-google-community` package
- Real-time internet search capability

---

## 4. DEPENDENCIES & REQUIREMENTS

### Python Packages (x86_64.txt)

**AI/ML Frameworks**:
- langchain>=0.2.16
- langchain-core>=0.2.38
- langchain-community>=0.2.16
- langchain-groq>=0.1.9 (Groq LLM API)
- langchain-openai>=0.1.23
- langchain-google-community>=1.0.8
- langchain-ollama>=0.1.0 (local LLM)

**Web Framework**:
- Flask>=3.0.3
- flask-sock>=0.7.0 (WebSocket support)
- websockets>=13.0
- requests>=2.32.3

**Audio Processing**:
- SpeechRecognition>=3.10.4
- pydub>=0.25.1 (audio format conversion)
- pyaudio>=0.2.14 (microphone/speaker I/O)

**API Integrations**:
- spotipy>=2.24.0 (Spotify)
- google-api-python-client>=2.122.0 (Calendar)
- google-auth-oauthlib>=1.2.1 (OAuth)
- google-auth-httplib2>=0.2.0
- google-cloud-texttospeech>=2.17.2 (TTS)

**ML Models**:
- torch>=2.4.0 (PyTorch for TTS/VAD)
- torchaudio>=2.4.0
- TTS>=0.22.0 (Coqui TTS)
- transformers>=4.44.0

**Configuration**:
- python-dotenv>=1.0.1 (.env loading)
- pyyaml>=6.0.1 (YAML config)
- pydantic>=2.0.0 (schema validation)

**Wake-Word & Utilities**:
- openwakeword>=0.5.1
- Pillow>=10.4.0 (image processing for display)

**Optional Local Models** (commented out, can be uncommented):
- faster-whisper>=1.0.0 (local STT)
- piper-tts>=1.2.0 (local TTS)

### Platform-Specific Notes

**ARM64.txt**:
- Same as x86_64 with additional comments
- Notes about optional packages for Raspberry Pi
- Hardware libs (RPi.GPIO, Jetson.GPIO, adafruit-circuitpython-ssd1306)

---

## 5. TRAINING PIPELINE

### CROS_2025 Directory

**Status**: Mentioned in CLAUDE.md but NOT present in current repo

The CLAUDE.md references a separate `CROS_2025/` subproject for wake-word training:

```bash
# Commands mentioned (not available):
cd CROS_2025

# Download datasets
python3 data_downloads/download_mit_rirs.py
python3 data_downloads/download_noise_and_fma_audio.py
./data_downloads/setup_openwakeword_resources.sh

# Generate synthetic data
python3 inference/infer_dataset.py --config configs/config.yaml
python3 inference/infer_dataset_negative.py --config configs/config.yaml

# Augmentation
python3 augment.py --training_config configs/my_model.yml --overwrite

# Training
python3 train.py --training_config configs/my_model.yml
```

**Current State**: Not present in the repository. The project uses pre-trained models:
- `custom_models/wake_word/Talos.onnx` (current)
- `custom_models/wake_word/ei_bmo.onnx` (alternative)

---

## 6. SETUP & UTILITY SCRIPTS

### setup_oww.py (50 lines)
- Downloads OpenWakeWord base models
- Determines venv path automatically
- Downloads to site-packages/openwakeword/resources/models
- Models downloaded:
  - melspectrogram.onnx
  - embedding_model.onnx

### list_audio_devices.py (183 lines)
- Comprehensive audio device enumeration
- Separates input (microphone) and output (speaker) devices
- Shows default devices
- Supports device testing
- Jetson-specific tips for USB/HDMI audio
- Usage: `python list_audio_devices.py [device_index] [input|output]`

### record_samples.py (in custom_models/)
- Utility for recording voice samples for Coqui TTS voice cloning

---

## 7. WEB INTERFACE

### index.html (105+ lines)

Browser-based BMO client with WebSocket communication:

**Features**:
- BMO-themed UI (green/dark color scheme)
- Simple recording button with pulse animation
- Real-time status display
- WebSocket auto-reconnection (3-second retry)
- WebM audio format support
- Audio playback of responses
- Responsive design with mobile support

**Flow**:
1. Connect to WebSocket endpoint (`/audio`)
2. User clicks microphone button to record
3. Browser captures audio via MediaRecorder API
4. Sends WebM blob to server
5. Server processes and responds with MP3/WAV
6. Browser plays response audio

---

## 8. DOCUMENTATION

### In docs/ directory (3,327 lines total):

1. **JETSON_ORIN_DEPLOYMENT.md** (662 lines)
   - Complete Jetson Orin deployment guide
   - Performance tuning (MAXN mode, jetson_clocks)
   - RAM/swap configuration
   - Model recommendations per device
   - GPU settings
   - Expected latencies

2. **AUDIO_DEVICES.md** (464 lines)
   - Audio configuration troubleshooting
   - Device detection methods
   - Platform-specific audio setup

3. **LOCAL_MODELS.md** (307 lines)
   - Local LLM setup (Ollama)
   - Local STT (faster-whisper)
   - Local TTS (Piper, Coqui)
   - Offline operation guide

4. **LOCAL_SETUP_QUICK_START.md** (377 lines)
   - Quick reference for local model setup
   - Performance tuning tips

5. **TTS_COMPARISON.md** (345 lines)
   - Comparison of TTS engines
   - Quality vs. speed tradeoffs
   - Voice cloning capabilities

6. **ARCHITECTURE_FLEXIBILITY.md** (417 lines)
   - Architecture design patterns
   - How to swap components
   - Adding new tools/services

7. **INSTALL_SCRIPT_EXPLAINED.md** (755 lines)
   - Step-by-step installation guide
   - Dependency explanations
   - Troubleshooting common issues

---

## 9. KEY IMPLEMENTATION DETAILS

### Audio Pipeline

**Recording Flow**:
1. Microphone → PyAudio stream
2. OpenWakeWord detection loop (80ms chunks)
3. On wake-word trigger:
   - Clear buffer (500ms default)
   - Activate VAD-based recording
   - Or fixed-duration recording if VAD disabled
4. Save to WAV file (16kHz, mono, int16)

**Transcription Flow**:
1. Load audio file
2. Try local STT (if configured)
3. Fallback to cloud STT if local fails/unavailable
4. Return transcribed text

**TTS Flow**:
1. Generate audio based on engine:
   - Google: HTTP request → MP3
   - Coqui: Load model + synthesize → WAV
   - Piper: Subprocess command → WAV
2. Save to file
3. Load file and play via PyAudio or pydub

### Session Management

**BMO.py (Persistent Session)**:
- Generates UUID-based session ID at startup
- Same session ID used for entire runtime
- All conversation memory within this session
- Lost on restart (in-memory storage)

**bmo_server.py (Per-Connection Session)**:
- Currently uses default session for all connections
- Could be enhanced to use unique session per client

**Memory Storage**:
- `SESSION_HISTORIES` dict in memory.py
- Each session → ChatMessageHistory instance
- Could be replaced with Redis/database for persistence

### Credentials Handling

**Google ADC** (Application Default Credentials):
- Path: `google_adc_credentials.json` (project root)
- Set before importing Google libraries
- Used by: TTS, Search, Calendar
- Both entry points check and set this

**Google OAuth** (Calendar):
- Credentials: `credentials.json` (project root)
- Token: `token.json` (created on first auth)
- Desktop app flow (not web app)

**Spotify OAuth**:
- Client ID/Secret from .env
- Redirect URI: http://127.0.0.1:9090
- Stored in .cache directory

---

## 10. ARCHITECTURAL PATTERNS & BEST PRACTICES

### Modern AI Agent Patterns Used

1. **Tool Calling Agent**: LangChain's `create_openai_tools_agent`
2. **Structured Output**: Pydantic models for agent decisions
3. **Runnable Chains**: LangChain's Runnable pattern for composability
4. **Message History**: `RunnableWithMessageHistory` for memory
5. **Singleton Configuration**: Centralized config with lazy initialization
6. **Adaptive Audio**: VAD for intelligent speech detection
7. **Hybrid Processing**: Cloud + local fallback patterns
8. **Hardware Abstraction**: Auto-detection with simulation modes

### Code Quality Observations

**Strengths**:
- Type hints throughout
- Comprehensive error handling
- Pydantic validation ensures correctness
- Modular architecture with clear separation
- Well-documented configuration system
- Extensive logging and debug output
- Support for multiple deployment platforms
- Graceful degradation on missing hardware
- Conditional tool loading
- Lazy model initialization

**Areas for Improvement**:
- Legacy wake_word_detector.py (using PicoVoice, not OpenWakeWord)
- No database persistence for conversation history
- Per-connection session management could be enhanced
- Some hardcoded constants (e.g., LED pin 17)
- Limited error recovery in audio pipeline
- No input validation on user prompts to LLM

---

## 11. ANALYSIS OF CLAUDE.md ACCURACY

### Outdated/Incorrect Information Found:

1. **CROS_2025 Directory**: 
   - CLAUDE.md describes detailed training pipeline
   - **REALITY**: Directory does not exist in current repo
   - The training pipeline commands are documented but unavailable

2. **Wake-Word Detector**:
   - CLAUDE.md describes "WakeWordDetector" in services
   - **REALITY**: Current code uses OpenWakeWord directly in BMO.py
   - wake_word_detector.py exists but is deprecated (uses PicoVoice)

3. **Configuration Example**:
   - CLAUDE.md shows old-style config format
   - **REALITY**: Current config has expanded structure with mode selection (cloud/local/hybrid)
   - Old format is simpler but new format is more flexible

4. **Tool Descriptions**:
   - CLAUDE.md mentions "ferramentas" and "conversa" routing
   - **REALITY**: Confirmed accurate - router makes this distinction
   - Portuguese terminology correctly described

### Accurate Information:

- Configuration system (YAML + Pydantic): Correct
- Three-tier architecture (router, conversation, tools): Accurate
- Memory management approach: Correct
- Tool implementation methods: Accurate
- Entry points (BMO.py, bmo_server.py): Correct
- Credential handling: Accurate
- Hardware abstraction: Correct
- Services layer design: Accurate

---

## 12. DIRECTORY STRUCTURE SUMMARY

```
Total Python Files: 19
- Entry points: 2 (BMO.py, bmo_server.py)
- Agent/Memory: 2 (agent_executor.py, memory.py)
- Services: 4 (audio_manager, hardware, display, wake_word_detector)
- Tools: 3 (spotify, calendar, search) + 1 __init__
- Configuration: 6 (config_manager, settings, prompts, setup_oww, + 2 legacy)
- Utilities: 1 (list_audio_devices, record_samples)

Total Lines of Code (Python): ~2,000
- Config system: 469 lines
- Audio manager: 629 lines
- Agent executor: 238 lines
- All services: 151 lines
- Tools: 214 lines

Documentation: 3,327 lines (7 markdown files)
Configuration: YAML files for main config, Jetson config, prompts
Wake-word models: 2 ONNX files (410KB total)
Voice sample: 1 WAV file for TTS voice cloning
Web UI: 1 HTML file with embedded CSS/JavaScript
```

---

## 13. DEPLOYMENT PLATFORMS SUPPORTED

1. **PC/Desktop** (x86_64): Full support with all features
2. **Raspberry Pi** (ARM64): Full support, can use local models
3. **NVIDIA Jetson Orin** (ARM64 + GPU): Optimized with GPU acceleration
4. **Browser** (via bmo_server.py): Web-based interface

Each platform has specific optimization guidance in docs/.

---

## 14. NOTABLE IMPLEMENTATION DETAILS

### Smart Feature Selections

1. **Multiple TTS Engines**: User can choose based on latency/quality needs
2. **Hybrid Cloud/Local**: Automatically tries best option
3. **VAD Adaptive Recording**: No fixed duration needed for natural interaction
4. **Device Auto-Detection**: Works on PC, RPi, Jetson with same code
5. **Tool Conditional Loading**: Don't initialize tools user doesn't need
6. **Temperature Separation**: Different temperatures for router vs. conversation

### Performance Optimizations

1. **Lazy Model Loading**: VAD, TTS, STT loaded on first use
2. **GPU Support**: CUDA acceleration for torch-based operations
3. **Lighter Model Options**: Can use tiny/base whisper instead of large-v3
4. **Piper for Speed**: Lightweight TTS alternative to full Coqui
5. **Local Ollama**: No network latency for LLM (on supported devices)

### UX Considerations

1. **Personality**: All text responses in Portuguese with BMO personality
2. **Visual Feedback**: LED + OLED display show state changes
3. **Audio Buffer Clearing**: Prevents echo-based false triggers
4. **Speech Padding**: Natural recording boundaries
5. **Web UI**: Simple, clean, mobile-friendly interface

---

## CONCLUSION

The BMO project is a well-architected, production-ready voice assistant with:

- **Modern AI patterns**: Routing agents, tool calling, message history
- **Flexible deployment**: Cloud, local, or hybrid modes
- **Multiple platforms**: Desktop, RPi, Jetson with auto-detection
- **Professional configuration**: Type-safe YAML-based system
- **Clean architecture**: Clear separation of concerns
- **Comprehensive documentation**: 3,300+ lines of guides
- **Voice cloning**: Coqui TTS supports custom voices
- **Privacy options**: Can run 100% offline with local models

The codebase follows best practices for AI agent development and is well-suited for both hobbyist projects and professional deployments.

**Minor improvements** would include:
- Update/remove legacy PicoVoice detector
- Add database persistence for conversations
- Implement multi-user session management for server
- Consider constant extraction for hardcoded values
