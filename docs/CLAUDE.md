# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BMO is a production-ready personal voice assistant inspired by the Adventure Time character. It combines wake-word detection, speech recognition, LLM-based conversation, and tool integration (Spotify, Google Calendar, Google Search) with text-to-speech capabilities. The project uses a LangChain-based agent architecture with intelligent routing between conversation and tool execution.

**Architecture Philosophy:** BMO follows modern AI agent best practices with YAML-based configuration, Pydantic validation, type hints, and clear separation of concerns. It supports multiple deployment modes (cloud/local/hybrid) and platforms (PC, Raspberry Pi, NVIDIA Jetson).

## Development Commands

### Automated Installation (Recommended)

BMO provides automated installation scripts for easy setup:

**Desktop/PC (Ubuntu/Debian/Fedora/Arch):**
```bash
cd BMO-Project
bash requirements/install_desktop.sh
```
- Detects OS and installs dependencies automatically
- Creates virtual environment
- Installs Python packages
- Offers cloud/local/hybrid mode selection
- Optionally downloads Ollama and LLM models
- Configures audio devices
- Creates credentials directory

**NVIDIA Jetson Orin:**
```bash
cd BMO-Project
bash requirements/install_jetson.sh
```
- Verifies CUDA and PyTorch
- Installs GPU-accelerated dependencies
- Configures performance mode (MAXN, jetson_clocks)
- Downloads Ollama and local models
- Sets up optimized config for Jetson
- Creates swap if needed

**Docker (Server Mode):**
```bash
# Build and start
docker-compose up -d

# Access web interface
open http://localhost:5000

# See DOCKER.md for full guide
```

### Manual Setup

If you prefer manual installation or are on an unsupported platform:

```bash
# Install system dependencies (Linux/Raspberry Pi)
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg git python3-venv flac

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements/x86_64.txt  # PC
pip install -r requirements/ARM64.txt   # Raspberry Pi

# Download OpenWakeWord base models
python config/setup_oww.py

# Setup configuration files
cp config.yaml.example config/config.yaml
# Edit config/config.yaml with your settings

# Create credentials directory
mkdir -p credentials

# Create .env file with API keys
cp .env.example .env
# Edit .env with your API keys

# Place your Google Cloud credentials in the credentials/ directory:
# - credentials/google_adc_credentials.json (for TTS and Search)
# - credentials/credentials.json (for Calendar OAuth)
# The token.json file will be generated automatically on first auth
```

### Running the Application

```bash
# Standalone mode (with wake-word detection via microphone)
source venv/bin/activate  # If not using Docker
python app/BMO.py

# Web server mode (Flask + WebSocket for browser-based interaction)
source venv/bin/activate  # If not using Docker
python app/bmo_server.py

# Docker mode (server only)
docker-compose up -d

# List audio devices (useful for configuration)
python tutorials/list_audio_devices.py
```

## Configuration Architecture

### YAML-Based Configuration System

BMO uses a modern, type-safe configuration system following AI agent best practices:

**Configuration Files:**
- `config/config.yaml` - Main configuration (models, audio, tools, server)
- `config/prompts.yaml` - All LLM prompts and templates
- `.env` - API keys and secrets (not tracked in git)
- `config.yaml.example` - Template for users to copy and customize

**Configuration Manager:**
- `config/config_manager.py` - Centralized config loader with Pydantic validation
- Singleton pattern: `get_config()` returns the same instance across modules
- Type-safe access to all settings with autocomplete support
- Automatic environment variable management

**Legacy Compatibility:**
- `config/settings.py` - Legacy wrapper for backward compatibility
- `config/prompts.py` - Legacy wrapper for backward compatibility
- New code should use `get_config()` directly

### Key Configuration Sections

**LLM Settings** (`config.yaml` → llm):
- **Mode selection**: `cloud`, `local`, or `hybrid` (fallback support)
  - Cloud: Groq API with fast models (llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768)
  - Local: Ollama with GPU support on supported hardware
  - Hybrid: Try local first, fallback to cloud on failure
- Separate temperatures for router (0.0), agent (0.7), and conversation (0.7)
- Agent execution parameters (max_iterations, verbose, error handling)

**Audio Settings** (`config.yaml` → wake_word, recording, stt, tts):
- Wake-word detection parameters (threshold, model path, audio format)
- **VAD (Voice Activity Detection)**: Intelligent speech end detection using Silero VAD
- Recording with VAD or fixed duration modes
- Buffer management to prevent echo/false triggers
- **STT mode selection**: `cloud`, `local`, or `hybrid`
  - Cloud: Groq Whisper API (fast, accurate)
  - Local: faster-whisper with ONNX/CUDA support
  - Hybrid: Automatic fallback
- **TTS engine selection**: Google Cloud, Coqui (XTTS), Piper, or ElevenLabs
  - Google: High quality, cloud-dependent, multiple voices
  - Coqui: Free, local, GPU-accelerated, voice cloning support
  - Piper: Fast, lightweight, CPU-friendly
  - ElevenLabs: Premium quality (future support)

**Tool Integration** (`config.yaml` → spotify, google_calendar):
- OAuth scopes and redirect URIs
- Credentials file paths

**Prompts** (`config/prompts.yaml`):
- System prompt with personality (supports {user_name} template)
- Router template for intent classification
- Error messages and response templates

### Using Configuration in Code

```python
# Get configuration instance (singleton pattern)
from config.config_manager import get_config

config = get_config()

# Access typed configuration with autocomplete support
mode = config.config.llm.mode  # "cloud", "local", or "hybrid"
model_name = config.config.llm.cloud.model_name
threshold = config.config.wake_word.threshold
user_name = config.USER_NAME
tts_engine = config.config.tts.engine

# Get API keys from environment
groq_key = config.get_api_key("groq")
spotify_id = config.get_api_key("spotify_client_id")

# Get formatted prompts with template substitution
system_prompt = config.get_system_prompt()  # Auto-fills {user_name}
router_template = config.get_router_template()

# Get resolved paths (handles absolute/relative)
wake_word_path = config.get_wake_word_model_path()
temp_audio = config.get_path('temp_audio')
custom_models = config.get_path('custom_models')

# Check if tools are enabled
if config.is_tool_enabled("spotify"):
    # Load Spotify tools
    pass

# NEW: Get LLM instance based on configuration (cloud/local/hybrid)
# This automatically handles mode selection and fallback
router_llm = config.get_llm(temperature=0.0, purpose="router")
agent_llm = config.get_llm(temperature=0.7, purpose="agent")
conversation_llm = config.get_llm(temperature=0.7, purpose="conversation")
```

## Architecture

### Core Components

**Main Entry Points:**
- `app/BMO.py` - Autonomous mode with OpenWakeWord detection, audio recording, and local playback
- `app/bmo_server.py` - Flask server with WebSocket endpoint for web-based interaction

**Agent Brain (`bmo_core/agent/`):**
- `agent_executor.py` - LangChain agent with intelligent routing system
- `memory.py` - Session-based conversation memory using `RunnableWithMessageHistory`

**Services (`bmo_core/services/`):**
- `audio_manager.py` - Multi-engine STT (Groq/faster-whisper) and TTS (Google/Coqui/Piper) with VAD support
- `hardware_manager.py` - Hardware abstraction (LEDs, GPIO) with auto-detection
- `display_manager.py` - Display control (OLED screens, visual feedback with face expressions)
- `wake_word_detector.py` - **LEGACY** Picovoice-based detector (deprecated, use OpenWakeWord directly in BMO.py)

**Tools (`bmo_core/tools/`):**
- `spotify.py` - Play music, control playback, get current song
- `calendar.py` - Google Calendar integration for appointments
- `search.py` - Google Custom Search API wrapper

**Configuration (`config/`):**
- `config_manager.py` - Centralized YAML-based configuration with Pydantic validation
- `config.yaml` - Main configuration file
- `prompts.yaml` - LLM prompts and templates
- `settings.py` - Legacy compatibility wrapper
- `prompts.py` - Legacy compatibility wrapper
- `setup_oww.py` - Downloads OpenWakeWord base models

### The LangChain Routing Architecture

The agent uses a **three-tier architecture** with intelligent routing:

1. **Router Chain** (`router_chain`):
   - Uses ChatGroq with `temperature=0` (from config) and structured output
   - Analyzes user input + chat history
   - Returns `{"destination": "ferramentas"}` or `{"destination": "conversa"}`

2. **Conversation Chain** (`conversation_chain`):
   - Activated for general conversation, greetings, follow-up questions
   - Uses ChatGroq with configurable temperature (default 0.7)
   - Applies BMO personality from `prompts.yaml`

3. **Tool Agent Chain** (`tool_agent_chain`):
   - Activated when user requires external actions (music, calendar, search)
   - Uses `create_openai_tools_agent` with `hwchase17/openai-tools-agent` prompt
   - AgentExecutor with configurable max_iterations and error handling

**Memory Management:**
- All chains share the same `ChatMessageHistory` via `RunnableWithMessageHistory`
- Session ID determines conversation context (persistent per execution in BMO.py)
- Router has access to full chat history for context-aware routing

### Important Implementation Details

**Credentials Setup:**
- Google ADC credentials: `credentials/google_adc_credentials.json` (for TTS and Search)
- Google OAuth credentials: `credentials/credentials.json` (for Calendar)
- Google OAuth token: `credentials/token.json` (generated on first auth)
- Spotify cache: `.cache` directory (generated automatically)
- Both entry points set `GOOGLE_APPLICATION_CREDENTIALS` before importing Google libraries
- First run requires browser-based OAuth flow for Spotify and Calendar
- All credential files are in the `credentials/` directory and ignored by git

**Audio Pipeline:**
- All audio settings configurable in `config.yaml`
- Default: 16kHz, 1 channel, int16 format
- Wake-word chunk size: 1280 samples (80ms)
- **VAD-based adaptive recording**: Silero VAD model detects speech/silence automatically
  - Configurable thresholds and padding for natural boundaries
  - Max duration safety limit
  - Fallback to fixed-duration recording if VAD disabled
- Buffer clearing after playback prevents echo/false triggers
- Multi-device support with configurable input/output device indices

**Session Management:**
- `BMO.py`: Generates persistent UUID-based session ID for entire runtime
- `bmo_server.py`: Each WebSocket connection uses default session (could be enhanced for multi-user)
- Memory is in-memory only (lost on restart)

## Configuration Best Practices

**When modifying configuration:**
1. **Never commit secrets** - API keys go in `.env`, not YAML files
2. **Update Pydantic models** - If adding new config fields, update models in `config_manager.py`
3. **Provide defaults** - Use Pydantic Field defaults for optional settings
4. **Document in example** - Update `config.yaml.example` with comments
5. **Validate early** - Pydantic validates on load, catching errors before runtime

**When adding new features:**
1. Add configuration to appropriate YAML file (`config.yaml` or `prompts.yaml`)
2. Update Pydantic model in `config_manager.py`
3. Access via `get_config()` in your code
4. Update `config.yaml.example` template
5. Document in this file if architecturally significant

## Testing and Debugging

**Audio Device Selection:**
```bash
# List available audio devices
python -m sounddevice
```
Set `recording.input_device_index` in `config/config.yaml` to use a specific microphone.

**LangChain Debugging:**
Enable tracing in `config/config.yaml`:
```yaml
langchain:
  tracing_v2: true
  api_key: "your_langsmith_key"
  project: "bmo_debug"
```

**Configuration Validation:**
The ConfigManager validates all settings on load. If there's a configuration error, you'll see a Pydantic validation error with details about what's wrong.

**Common Issues:**
- If Google APIs fail: Verify `google_adc_credentials.json` exists and is valid
- If wake-word doesn't trigger: Adjust `wake_word.threshold` in config
- If audio playback blocks: Check buffer_clear_duration_ms setting
- If imports fail: Ensure `pyyaml` and `pydantic>=2.0` are installed

## Deployment Platforms

BMO supports multiple deployment platforms with optimized configurations:

**1. PC/Desktop (x86_64)**
- Full feature support with all cloud/local options
- Requirements: `requirements/x86_64.txt`
- Use default `config.yaml`

**2. Raspberry Pi (ARM64)**
- Full support with optional local model optimization
- Requirements: `requirements/ARM64.txt`
- Hardware support: GPIO LEDs, OLED displays (SSD1306)
- See: `docs/LOCAL_MODELS.md` for offline operation

**3. NVIDIA Jetson Orin (ARM64 + GPU)**
- GPU-accelerated local models for optimal performance
- Optimized config: `config/config.jetson.yaml`
- Coqui TTS with GPU acceleration
- faster-whisper with CUDA support
- Local Ollama LLM with GPU
- See: `docs/JETSON_ORIN_DEPLOYMENT.md`

**4. Web Browser (via bmo_server.py)**
- WebSocket-based interface
- Works on any device with modern browser
- Audio streaming from browser to server
- Responsive, mobile-friendly UI

**5. Docker (Server Mode)**
- Containerized deployment
- Isolated environment with all dependencies
- Recommended for server/web mode
- See: `DOCKER.md` for full guide
- Limitations: Audio device access more complex for standalone mode

## Documentation

Comprehensive documentation is available:

**Main Documentation:**
- **README.md** - Main project documentation and quick start
- **CLAUDE.md** (this file) - Development guide for Claude Code
- **DOCKER.md** - Docker/container deployment guide

**Technical Documentation in `docs/`:**
- **JETSON_ORIN_DEPLOYMENT.md** (662 lines) - Complete Jetson setup, performance tuning, GPU configuration
- **AUDIO_DEVICES.md** (464 lines) - Audio troubleshooting, device detection, platform-specific setup
- **LOCAL_MODELS.md** (307 lines) - Offline operation with local LLM/STT/TTS
- **LOCAL_SETUP_QUICK_START.md** (377 lines) - Quick reference for local models
- **TTS_COMPARISON.md** (345 lines) - TTS engine comparison and recommendations
- **ARCHITECTURE_FLEXIBILITY.md** (417 lines) - Design patterns, component swapping
- **INSTALL_SCRIPT_EXPLAINED.md** (755 lines) - Installation guide and troubleshooting

**Installation Resources in `requirements/`:**
- `install_desktop.sh` - Automated installation for PC/Desktop (Ubuntu/Debian/Fedora/Arch)
- `install_jetson.sh` - Automated installation for NVIDIA Jetson Orin

**Utilities in `tutorials/`:**
- `list_audio_devices.py` - Audio device enumeration utility
- Platform-specific guides and examples

## Architecture Notes for Development

- **Configuration Pattern**: Always use `get_config()` for new code. Legacy `settings`/`prompts` imports are deprecated.
- **Type Safety**: ConfigManager provides full type hints. Use IDE autocomplete.
- **Centralized LLM Creation**: Use `config.get_llm(temperature, purpose)` to create LLM instances - it handles cloud/local/hybrid mode automatically
- **Path Handling**: Use `config.get_path()` for all file paths - it handles absolute/relative resolution
- **Mode Selection**: LLM and STT support `cloud`/`local`/`hybrid` modes - always check mode in config
- **Tool Functions**: Must be decorated with `@tool` and include docstrings
- **Tool Loading**: Tools are conditionally loaded based on config - use `config.is_tool_enabled(tool_name)`
- **Router Prompts**: Edit `config/prompts.yaml` when adding new tool categories
- **Memory Isolation**: Different session IDs maintain separate conversation contexts
- **Error Handling**: Agent executor has configurable error handling via `config.yaml`
- **Hardware Abstraction**: Services auto-detect platform (RPi/Jetson/PC) and gracefully degrade
- **Lazy Loading**: VAD, local models, TTS engines load on first use for faster startup
- **Wake-Word Detection**: OpenWakeWord is integrated directly in `BMO.py` (not via wake_word_detector.py)

## File Structure

```
/home/miguel/BMO-Project/
├── app/                          # Entry points
│   ├── BMO.py                   # Standalone mode with wake-word
│   └── bmo_server.py            # Flask + WebSocket server
│
├── bmo_core/                    # Core functionality
│   ├── agent/
│   │   ├── agent_executor.py    # LangChain routing agent
│   │   └── memory.py            # Conversation memory
│   ├── services/
│   │   ├── audio_manager.py     # Multi-engine STT/TTS with VAD
│   │   ├── hardware_manager.py  # GPIO/LED control
│   │   ├── display_manager.py   # OLED display
│   │   └── wake_word_detector.py # LEGACY (Picovoice)
│   └── tools/
│       ├── spotify.py           # Spotify integration
│       ├── calendar.py          # Google Calendar
│       └── search.py            # Google Search
│
├── config/                      # Configuration system
│   ├── config_manager.py        # Pydantic-based config loader
│   ├── config.yaml              # Main config (DO NOT COMMIT)
│   ├── config.jetson.yaml       # Jetson-optimized config
│   ├── prompts.yaml             # LLM prompts
│   ├── settings.py              # Legacy wrapper
│   ├── prompts.py               # Legacy wrapper
│   └── setup_oww.py             # OpenWakeWord setup
│
├── custom_models/               # ML models
│   ├── wake_word/
│   │   ├── Talos.onnx           # Current wake-word model
│   │   └── ei_bmo.onnx          # Alternative model
│   ├── bmo_voice_sample.wav     # Voice cloning sample
│   └── record_samples.py        # Voice recording utility
│
├── credentials/                 # Credentials directory (DO NOT COMMIT)
│   ├── credentials.json         # Google OAuth credentials (Calendar)
│   ├── token.json               # Google OAuth token (auto-generated)
│   └── google_adc_credentials.json  # Google Cloud ADC (TTS/Search)
│
├── docs/                        # Documentation (3,300+ lines)
├── tutorials/                   # Utility scripts
├── web/                         # Web interface
│   └── index.html               # Browser UI
│
├── requirements/
│   ├── x86_64.txt               # PC requirements
│   ├── ARM64.txt                # RPi/Jetson requirements
│   ├── install_desktop.sh       # Automated setup for PC
│   └── install_jetson.sh        # Automated setup for Jetson
│
├── config.yaml.example          # Config template (COMMIT)
├── .env                         # API keys (DO NOT COMMIT)
├── .env.example                 # Environment template (COMMIT)
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose config
├── docker-entrypoint.sh         # Docker startup script
├── .dockerignore                # Docker build exclusions
└── DOCKER.md                    # Docker usage guide
```

## Key Implementation Patterns

**1. Hybrid Cloud/Local Architecture**
- All major components (LLM, STT, TTS) support cloud/local/hybrid modes
- Hybrid mode tries local first, automatically falls back to cloud
- Enables offline operation and reduces latency/costs

**2. Voice Activity Detection (VAD)**
- Silero VAD model for intelligent speech detection
- No need for fixed recording duration
- Configurable thresholds and padding
- Lazy loading for faster startup

**3. Configuration-Driven Design**
- All behavior controlled via YAML files
- Pydantic validation catches errors at startup
- Tools conditionally loaded based on config
- Easy to disable features without code changes

**4. Hardware Abstraction**
- Auto-detects platform (PC/RPi/Jetson)
- Graceful degradation when hardware unavailable
- Same codebase works everywhere

**5. Memory Management**
- Session-based conversation history
- In-memory storage (lost on restart)
- Could be enhanced with Redis/database for persistence

**6. Multi-Engine Support**
- Multiple TTS engines with different tradeoffs (quality/speed/offline)
- Multiple STT providers (cloud/local)
- Cloud (Groq) and local (Ollama) LLMs

## Performance & Optimization

**Startup Optimization:**
- Lazy loading of heavy models (VAD, TTS, local STT)
- Configuration validated once at startup
- Singleton pattern for shared resources

**Runtime Optimization:**
- VAD prevents unnecessary processing
- Buffer clearing prevents echo-triggered loops
- Temperature separation (router=0, conversation=0.7)
- GPU acceleration where available

**Platform-Specific:**
- Jetson: MAXN mode, jetson_clocks, optimized models
- RPi: Lightweight models, CPU-optimized
- PC: Full cloud features for best quality

## File Naming Conventions

- Main scripts: `BMO.py`, `bmo_server.py` (mixed case preserved for branding)
- Modules: snake_case (e.g., `agent_executor.py`, `audio_manager.py`, `config_manager.py`)
- Config files: snake_case (e.g., `config.yaml`, `prompts.yaml`)
- Wake-word models: `.onnx` format in `custom_models/wake_word/`

## Code Quality & Best Practices

**Strengths:**
- Type hints throughout for better IDE support
- Comprehensive error handling with personality-consistent responses
- Pydantic validation ensures configuration correctness
- Modular architecture with clear separation of concerns
- Extensive documentation (3,300+ lines)
- Support for multiple deployment platforms
- Graceful degradation on missing hardware
- Conditional tool loading
- Lazy model initialization

**Areas for Enhancement:**
- Legacy `wake_word_detector.py` should be removed or updated
- No database persistence for conversation history
- Per-connection session management could be enhanced in server mode
- Some hardcoded constants (e.g., LED pin 17)
- Could add input validation/sanitization for LLM prompts
