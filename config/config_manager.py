"""
Configuration Manager for BMO
Centralized configuration loading and validation using YAML and Pydantic.
Follows best practices for AI Agent development with LangChain.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class ProjectConfig(BaseModel):
    """Project metadata configuration."""
    name: str
    version: str
    user_name: str


class LLMTemperatures(BaseModel):
    """Temperature settings for different LLM use cases."""
    router: float = Field(ge=0.0, le=2.0)
    agent: float = Field(ge=0.0, le=2.0)
    conversation: float = Field(ge=0.0, le=2.0)


class AgentConfig(BaseModel):
    """Agent execution configuration."""
    max_iterations: int = Field(gt=0)
    verbose: bool
    handle_parsing_errors: bool


class LLMCloudConfig(BaseModel):
    """Cloud LLM configuration."""
    provider: str = "groq"
    model_name: str


class AirLLMConfig(BaseModel):
    """AirLLM specific configuration."""
    hf_repo: str
    compression: Optional[str] = None
    max_length: int = 128


class LLMLocalConfig(BaseModel):
    """Local LLM configuration."""
    provider: str = "ollama"
    model: str
    base_url: str = "http://localhost:11434"
    timeout: int = 120
    airllm: Optional[AirLLMConfig] = None


class LLMConfig(BaseModel):
    """LLM provider and model configuration."""
    mode: str = Field(pattern="^(cloud|local|hybrid)$")
    cloud: LLMCloudConfig
    local: LLMLocalConfig
    temperatures: LLMTemperatures
    agent: AgentConfig


class CoquiTTSConfig(BaseModel):
    """Coqui TTS configuration."""
    model: str
    voice_sample_path: str
    language: str
    split_sentences: bool


class PiperTTSConfig(BaseModel):
    """Piper TTS configuration."""
    voice: str = "pt_BR-faber-medium"
    quality: str = "medium"
    speaker: Optional[int] = None
    length_scale: float = 1.0


class ElevenLabsTTSConfig(BaseModel):
    """ElevenLabs TTS configuration."""
    voice_id: Optional[str] = None


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""
    engine: str
    coqui: CoquiTTSConfig
    piper: PiperTTSConfig
    elevenlabs: ElevenLabsTTSConfig


class STTCloudConfig(BaseModel):
    """Cloud STT configuration."""
    provider: str = "groq"
    model: str
    language: str


class STTLocalConfig(BaseModel):
    """Local STT configuration."""
    provider: str = "faster-whisper"
    model: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "pt"
    beam_size: int = 5


class STTConfig(BaseModel):
    """Speech-to-Text configuration."""
    mode: str = Field(pattern="^(cloud|local|hybrid)$")
    cloud: STTCloudConfig
    local: STTLocalConfig


class WakeWordAudioConfig(BaseModel):
    """Audio settings for wake word detection."""
    sample_rate: int
    chunk_size: int
    channels: int
    format: str


class WakeWordConfig(BaseModel):
    """Wake word detection configuration."""
    model_path: str
    threshold: float = Field(ge=0.0, le=1.0)
    inference_framework: str
    audio: WakeWordAudioConfig


class VADConfig(BaseModel):
    """Voice Activity Detection configuration."""
    enabled: bool = True
    threshold: float = Field(ge=0.0, le=1.0, default=0.5)
    min_speech_duration_ms: int = Field(gt=0, default=250)
    min_silence_duration_ms: int = Field(gt=0, default=700)
    max_recording_seconds: int = Field(gt=0, default=30)
    speech_pad_ms: int = Field(ge=0, default=300)


class RecordingConfig(BaseModel):
    """Audio recording configuration."""
    duration_seconds: int
    sample_rate: int
    channels: int
    chunk_size: int
    format: str
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None
    buffer_clear_duration_ms: int
    vad: VADConfig


class ToolEnabledConfig(BaseModel):
    """Individual tool enable/disable configuration."""
    enabled: bool = True


class ToolsConfig(BaseModel):
    """Tools enable/disable configuration."""
    spotify: ToolEnabledConfig
    google_calendar: ToolEnabledConfig
    google_search: ToolEnabledConfig


class SpotifyConfig(BaseModel):
    """Spotify integration configuration."""
    scope: str
    redirect_uri: str


class GoogleCalendarConfig(BaseModel):
    """Google Calendar integration configuration."""
    credentials_file: str
    token_file: str
    scopes: List[str]


class ServerConfig(BaseModel):
    """Flask server configuration."""
    host: str
    port: int
    debug: bool


class LangChainConfig(BaseModel):
    """LangChain settings."""
    tracing_v2: bool
    api_key: str
    endpoint: str
    project: str


class PathsConfig(BaseModel):
    """Paths configuration."""
    base_dir: str
    temp_audio: str
    response_audio_mp3: str
    response_audio_wav: str
    web_folder: str
    custom_models: str


class DisplayConfig(BaseModel):
    """Display configuration."""
    enabled: bool
    type: Optional[str] = None
    width: int
    height: int


class HardwareConfig(BaseModel):
    """Hardware configuration."""
    enabled: bool
    gpio_led_pin: Optional[int] = None
    display: DisplayConfig


class PromptsConfig(BaseModel):
    """Prompts configuration."""
    system_prompt: str
    router_template: str
    tools: Dict[str, Any]
    errors: Dict[str, str]
    responses: Dict[str, str]


class BMOConfig(BaseModel):
    """Main BMO configuration model."""
    project: ProjectConfig
    llm: LLMConfig
    tts: TTSConfig
    stt: STTConfig
    wake_word: WakeWordConfig
    recording: RecordingConfig
    tools: ToolsConfig
    spotify: SpotifyConfig
    google_calendar: GoogleCalendarConfig
    server: ServerConfig
    langchain: LangChainConfig
    paths: PathsConfig
    hardware: HardwareConfig


class ConfigManager:
    """
    Centralized configuration manager for BMO.
    Loads and validates YAML configurations, manages environment variables,
    and provides type-safe access to all settings.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Path to configuration directory. Defaults to 'config' in project root.
        """
        # Determine base directory
        if config_dir is None:
            # Go up from config_manager.py -> config -> BMO-Project
            self.base_dir = Path(__file__).resolve().parent.parent
            self.config_dir = self.base_dir / "config"
        else:
            self.config_dir = Path(config_dir)
            self.base_dir = self.config_dir.parent

        # Load environment variables
        env_path = self.base_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            print(f"⚠️  Warning: .env file not found at {env_path}")

        # Load configurations
        self.config = self._load_config()
        self.prompts = self._load_prompts()

        # Set base_dir in paths config
        self.config.paths.base_dir = str(self.base_dir)

        # Setup environment variables
        self._setup_environment()

        print(f"✅ Configuration loaded successfully (BMO v{self.config.project.version})")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from the config directory."""
        file_path = self.config_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_config(self) -> BMOConfig:
        """Load and validate main configuration."""
        config_data = self._load_yaml("config.yaml")
        return BMOConfig(**config_data)

    def _load_prompts(self) -> PromptsConfig:
        """Load and validate prompts configuration."""
        prompts_data = self._load_yaml("prompts.yaml")
        return PromptsConfig(**prompts_data)

    def _setup_environment(self):
        """Setup environment variables from .env and config."""
        # Set LangChain environment variables
        os.environ["LANGCHAIN_TRACING_V2"] = str(self.config.langchain.tracing_v2).lower()
        if self.config.langchain.api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.config.langchain.api_key
        os.environ["LANGCHAIN_ENDPOINT"] = self.config.langchain.endpoint
        os.environ["LANGCHAIN_PROJECT"] = self.config.langchain.project



    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key from environment variables.

        Args:
            service: Service name (groq, google, spotify_client_id, etc.)

        Returns:
            API key or None if not found
        """
        env_map = {
            "groq": "GROQ_API_KEY",
            "google": "GOOGLE_API_KEY",
            "google_cse_id": "GOOGLE_CSE_ID",
            "spotify_client_id": "SPOTIPY_CLIENT_ID",
            "spotify_client_secret": "SPOTIPY_CLIENT_SECRET",
            "elevenlabs": "ELEVEN_LABS_API_KEY",
            "langchain": "LANGCHAIN_API_KEY",
        }

        env_var = env_map.get(service)
        if not env_var:
            raise ValueError(f"Unknown service: {service}")

        value = os.getenv(env_var)
        if not value:
            print(f"⚠️  Warning: {env_var} not found in environment")
        return value

    def get_system_prompt(self) -> str:
        """Get the formatted system prompt with user name."""
        return self.prompts.system_prompt.format(
            user_name=self.config.project.user_name
        )

    def get_router_template(self) -> str:
        """Get the router template."""
        return self.prompts.router_template

    def get_path(self, path_key: str) -> Path:
        """
        Get a resolved path from paths configuration.

        Args:
            path_key: Key from paths config (e.g., 'temp_audio', 'web_folder')

        Returns:
            Resolved Path object
        """
        path_str = getattr(self.config.paths, path_key)
        path = Path(path_str)

        # If not absolute, make it relative to base_dir
        if not path.is_absolute():
            path = self.base_dir / path

        return path

    def get_wake_word_model_path(self) -> Path:
        """Get the full path to the wake word model."""
        model_path = Path(self.config.wake_word.model_path)
        if not model_path.is_absolute():
            model_path = self.base_dir / model_path
        return model_path

    def get_tts_voice_sample_path(self) -> Optional[Path]:
        """Get the full path to TTS voice sample (for Coqui)."""
        if self.config.tts.engine != "coqui":
            return None

        sample_path = Path(self.config.tts.coqui.voice_sample_path)
        if not sample_path.is_absolute():
            sample_path = self.base_dir / sample_path
        return sample_path

    @property
    def BASE_DIR(self) -> Path:
        """Get base directory as Path object."""
        return self.base_dir

    @property
    def BMO_VERSION(self) -> str:
        """Get BMO version."""
        return self.config.project.version

    @property
    def USER_NAME(self) -> str:
        """Get configured user name."""
        return self.config.project.user_name

    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        Check if a tool is enabled.

        Args:
            tool_name: Name of the tool (spotify, google_calendar, google_search)

        Returns:
            True if tool is enabled, False otherwise
        """
        tool_config = getattr(self.config.tools, tool_name, None)
        if tool_config is None:
            print(f"⚠️  Warning: Unknown tool '{tool_name}'")
            return False
        return tool_config.enabled

    def get_llm(self, temperature: float, purpose: str = "general"):
        """
        Create and return an LLM instance based on configuration mode.

        Args:
            temperature: Temperature setting for the LLM
            purpose: Purpose of the LLM (for logging) - 'router', 'agent', 'conversation'

        Returns:
            LLM instance (ChatGroq or ChatOllama)
        """
        from langchain_groq import ChatGroq

        llm_config = self.config.llm
        mode = llm_config.mode.lower()

        # Try local first if hybrid mode
        if mode in ["local", "hybrid"]:
            try:
                return self._create_local_llm(temperature, purpose)
            except Exception as e:
                if mode == "local":
                    raise RuntimeError(f"Failed to initialize local LLM: {e}")
                print(f"⚠️  Local LLM failed, falling back to cloud: {e}")

        # Cloud mode or hybrid fallback
        return self._create_cloud_llm(temperature, purpose)

    def _create_local_llm(self, temperature: float, purpose: str):
        """Create local LLM (Ollama or AirLLM)."""
        llm_config = self.config.llm.local
        provider = llm_config.provider.lower()

        if provider == "airllm":
            try:
                from bmo_core.agent.airllm_wrapper import AirLLMWrapper
            except ImportError:
                raise ImportError("Failed to import AirLLMWrapper. Check dependencies.")
            
            print(f"   🖥️  Usando LLM local: AirLLM ({llm_config.airllm.hf_repo}) para {purpose}")
            return AirLLMWrapper(
                hf_repo=llm_config.airllm.hf_repo,
                compression=llm_config.airllm.compression,
                max_length=llm_config.airllm.max_length,
                max_new_tokens=150
            )

        # Fallback to Ollama
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain-ollama not installed. Run: pip install langchain-ollama")

        print(f"   🖥️  Usando LLM local: {llm_config.model} (Ollama) para {purpose}")
        return ChatOllama(
            model=llm_config.model,
            base_url=llm_config.base_url,
            temperature=temperature,
            timeout=llm_config.timeout
        )

    def _create_cloud_llm(self, temperature: float, purpose: str):
        """Create cloud LLM (Groq)."""
        from langchain_groq import ChatGroq

        groq_api_key = self.get_api_key("groq")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        llm_config = self.config.llm.cloud
        print(f"   ☁️  Usando LLM cloud: {llm_config.model_name} (Groq) para {purpose}")

        return ChatGroq(
            temperature=temperature,
            model_name=llm_config.model_name,
            groq_api_key=groq_api_key
        )


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get or create the singleton ConfigManager instance.

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> ConfigManager:
    """
    Force reload of configuration.

    Returns:
        New ConfigManager instance
    """
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager
