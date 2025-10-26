"""
Legacy settings module for backward compatibility.
New code should use config_manager.get_config() instead.

This module provides the same interface as the old settings.py,
but now loads all values from the YAML-based configuration system.
"""

from config.config_manager import get_config

# Load configuration
_config = get_config()

# --- Versão do Projeto ---
BMO_VERSION = _config.BMO_VERSION

# --- Base Directory ---
BASE_DIR = str(_config.BASE_DIR)

# --- Chaves de API (from environment variables) ---
print("🔑 Carregando chaves de API do .env...")
GROQ_API_KEY = _config.get_api_key("groq")
GOOGLE_API_KEY = _config.get_api_key("google")
GOOGLE_CSE_ID = _config.get_api_key("google_cse_id")
SPOTIPY_CLIENT_ID = _config.get_api_key("spotify_client_id")
SPOTIPY_CLIENT_SECRET = _config.get_api_key("spotify_client_secret")
ELEVEN_LABS_API_KEY = _config.get_api_key("elevenlabs")

# --- TTS Configuration ---
TTS_ENGINE = _config.config.tts.engine
GOOGLE_TTS_VOICE_NAME = _config.config.tts.google.voice_name
COQUI_VOICE_SAMPLE_PATH = str(_config.get_tts_voice_sample_path()) if _config.get_tts_voice_sample_path() else ""

# --- User Configuration ---
USER_NAME = _config.USER_NAME

# Note: Environment variables for LangChain are already set by ConfigManager
