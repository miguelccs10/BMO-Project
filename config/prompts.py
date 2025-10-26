"""
Legacy prompts module for backward compatibility.
New code should use config_manager.get_config() instead.

This module provides the same interface as the old prompts.py,
but now loads all prompts from the YAML-based configuration system.
"""

from config.config_manager import get_config

# Load configuration
_config = get_config()

# --- Main System Prompt ---
BMO_SYSTEM_PROMPT = _config.get_system_prompt()

# --- Router Template ---
ROUTER_TEMPLATE = _config.get_router_template()

# --- Error Messages ---
BRAIN_ERROR = _config.prompts.errors["brain_error"]
AGENT_ERROR = _config.prompts.errors["agent_error"]
PARSING_ERROR = _config.prompts.errors["parsing_error"]
AUDIO_EMPTY_ERROR = _config.prompts.errors["audio_empty"]

# --- Response Templates ---
AUDIO_SYSTEM_OFFLINE = _config.prompts.responses["audio_system_offline"]
TTS_OFFLINE = _config.prompts.responses["tts_offline"]
SPOTIFY_OFFLINE = _config.prompts.responses["spotify_offline"]
NO_SPOTIFY_DEVICE = _config.prompts.responses["no_spotify_device"]
