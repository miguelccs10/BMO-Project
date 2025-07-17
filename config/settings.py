# config/settings.py
# Ponto central para todas as configurações e chaves de API do projeto.
# Versão de Projeto: 5.0

import os
from dotenv import load_dotenv

# --- Carregamento do .env ---
# Define o caminho para a raiz do projeto para encontrar o arquivo .env
# Isso garante que funcione, não importa de onde o script seja chamado.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# --- Versão do Projeto ---
BMO_VERSION = "4.0"

# --- Chaves de API ---
print("🔑 Carregando chaves de API do .env...")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

# --- Configuração de Rastreamento (para remover avisos) ---
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

# --- Configuração do Motor de Voz (TTS) ---
# Opções: "google", "coqui", "elevenlabs"
TTS_ENGINE = "google"
GOOGLE_TTS_VOICE_NAME = "pt-BR-Wavenet-B"
COQUI_VOICE_SAMPLE_PATH = os.path.join(BASE_DIR, "bmo_voice_sample.wav")

# --- Nome do Usuário ---
USER_NAME = "Miguel"