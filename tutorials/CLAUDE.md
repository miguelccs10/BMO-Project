# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BMO is a personal voice assistant inspired by the Adventure Time character. It combines wake-word detection, speech recognition, LLM-based conversation, and tool integration (Spotify, Google Calendar, Google Search) with text-to-speech capabilities. The project uses a LangChain-based agent architecture with intelligent routing between conversation and tool execution.

**Architecture Philosophy:** BMO follows modern AI agent best practices with YAML-based configuration, Pydantic validation, type hints, and clear separation of concerns.

## Development Commands

### Initial Setup

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

# Create .env file with API keys
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Standalone mode (with wake-word detection via microphone)
python app/BMO.py

# Web server mode (Flask + WebSocket for browser-based interaction)
python app/bmo_server.py
```

### CROS_2025 Wake-Word Training Pipeline

The `CROS_2025/` directory is a separate subproject for custom wake-word model training:

```bash
cd CROS_2025

# Download required datasets
python3 data_downloads/download_mit_rirs.py
python3 data_downloads/download_noise_and_fma_audio.py
./data_downloads/setup_openwakeword_resources.sh

# Generate synthetic training data
python3 inference/infer_dataset.py --config configs/config.yaml
python3 inference/infer_dataset_negative.py --config configs/config.yaml

# Apply data augmentation
python3 augment.py --training_config configs/my_model.yml --overwrite

# Train the model
python3 train.py --training_config configs/my_model.yml
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
- Model selection (Groq models)
- Separate temperatures for router, agent, and conversation
- Agent execution parameters (max_iterations, verbose, error handling)

**Audio Settings** (`config.yaml` → wake_word, recording, stt, tts):
- Wake-word detection parameters (threshold, model path, audio format)
- Recording duration and buffer management
- STT provider and model selection
- TTS engine selection (Google, Coqui, ElevenLabs) with engine-specific configs

**Tool Integration** (`config.yaml` → spotify, google_calendar):
- OAuth scopes and redirect URIs
- Credentials file paths

**Prompts** (`config/prompts.yaml`):
- System prompt with personality (supports {user_name} template)
- Router template for intent classification
- Error messages and response templates

### Using Configuration in Code

```python
# Get configuration instance
from config.config_manager import get_config

config = get_config()

# Access typed configuration
model_name = config.config.llm.model_name
threshold = config.config.wake_word.threshold
user_name = config.USER_NAME

# Get API keys from environment
groq_key = config.get_api_key("groq")

# Get formatted prompts
system_prompt = config.get_system_prompt()  # Auto-fills user_name

# Get resolved paths
wake_word_path = config.get_wake_word_model_path()
temp_audio = config.get_path('temp_audio')
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
- `audio_manager.py` - STT (Whisper via Groq) and TTS (Google/Coqui/ElevenLabs)
- `wake_word_detector.py` - OpenWakeWord integration
- `hardware_manager.py` - Hardware abstraction (LEDs, GPIO)
- `display_manager.py` - Display control (screens, visual feedback)

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
- Google ADC credentials: `google_adc_credentials.json` in project root (for TTS and Search)
- Google OAuth credentials: `credentials.json` in project root (for Calendar)
- Both entry points set `GOOGLE_APPLICATION_CREDENTIALS` before importing Google libraries
- First run requires browser-based OAuth flow for Spotify and Calendar

**Audio Pipeline:**
- All audio settings configurable in `config.yaml`
- Default: 16kHz, 1 channel, int16 format
- Wake-word chunk size: 1280 samples (80ms)
- Recording duration: configurable (default 5 seconds)
- Buffer clearing after playback prevents echo/false triggers

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

## Architecture Notes for Development

- **Configuration Pattern**: Always use `get_config()` for new code. Legacy `settings`/`prompts` imports are deprecated.
- **Type Safety**: ConfigManager provides full type hints. Use IDE autocomplete.
- **Path Handling**: Use `config.get_path()` for all file paths - it handles absolute/relative resolution
- **Tool Functions**: Must be decorated with `@tool` and include docstrings
- **Router Prompts**: Edit `config/prompts.yaml` when adding new tool categories
- **Memory Isolation**: Different session IDs maintain separate conversation contexts
- **Error Handling**: Agent executor has configurable error handling via `config.yaml`

## File Structure for Configuration

```
config/
├── config.yaml          # Main configuration (DO NOT COMMIT with secrets)
├── prompts.yaml         # LLM prompts and templates
├── config_manager.py    # Configuration loader with Pydantic models
├── settings.py          # Legacy compatibility wrapper
├── prompts.py           # Legacy compatibility wrapper
└── setup_oww.py         # OpenWakeWord model downloader

config.yaml.example      # Template to copy (COMMIT THIS)
.env                     # API keys and secrets (DO NOT COMMIT)
.env.example             # Template for .env (COMMIT THIS)
```

## File Naming Conventions

- Main scripts: `BMO.py`, `bmo_server.py` (mixed case preserved for branding)
- Modules: snake_case (e.g., `agent_executor.py`, `audio_manager.py`, `config_manager.py`)
- Config files: snake_case (e.g., `config.yaml`, `prompts.yaml`)
- Wake-word models: `.onnx` format in `custom_models/wake_word/`
