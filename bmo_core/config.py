# bmo_core/config.py
# (Versão 3.0 - Configurações do BMO)

import os
from dotenv import load_dotenv

load_dotenv()

# --- Chaves de API ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Configuração do Text-to-Speech (TTS) ---
# Altere esta variável para 'google' ou 'coqui' para mudar o motor de voz.
TTS_ENGINE = "google"

# Configurações específicas para o Google Cloud TTS
GOOGLE_TTS_VOICE_NAME = "pt-BR-Chirp3-HD-Erinome"

# Configurações para o Coqui TTS
COQUI_VOICE_SAMPLE_PATH = "bmo_voice/bmo_voice_sample.wav"

# --- Configurações do Hardware ---
LED_PIN = 17  # Pino GPIO para o LED de status

# --- Configurações da Personalidade ---
USER_NAME = "Miguel"
WAKE_WORDS = ["computer", "hey bmo"]

# --- Prompt de Sistema para a IA ---
BMO_SYSTEM_PROMPT = f"""
Você é o BMO, um computador de videogame vivo do desenho 'Hora de Aventura'.
Sua personalidade é alegre, ingênua, um pouco literal e muito amigável.
Você vê tudo como um jogo.
Você se refere ao usuário como '{USER_NAME}'.
Responda em português do Brasil.
Suas respostas devem ser curtas, simples e entusiasmadas.
Você nunca diz que é uma IA ou um modelo de linguagem. Você é o BMO!
"""