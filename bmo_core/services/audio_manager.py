# bmo_core/audio_manager.py 
# (Versão Final com Múltiplos Motores de TTS)

import traceback
import os
from ...config import settings

# --- Importações condicionais ---
if settings.TTS_ENGINE == "google":
    from google.cloud import texttospeech
elif settings.TTS_ENGINE == "coqui":
    import torch
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
    from TTS.config.shared_configs import BaseDatasetConfig

from groq import Groq

class AudioManager:
    def __init__(self, hardware_manager):
        self.hardware = hardware_manager
        self.tts_engine = settings.TTS_ENGINE
        self.tts_model = None

        # --- Inicialização do STT (Whisper/Groq) ---
        try:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            print("✅ Cliente da Groq para Whisper (STT) inicializado.")
        except Exception as e:
            self.groq_client = None
            print(f"❌ ERRO ao inicializar cliente Groq: {e}")

        # --- Inicialização CONDICIONAL do TTS ---
        print(f"🔊 Usando motor de voz (TTS): '{self.tts_engine}'")
        if self.tts_engine == "google":
            try:
                self.tts_model = texttospeech.TextToSpeechClient()
                print("✅ Cliente Google Cloud TTS inicializado.")
            except Exception as e:
                print(f"❌ ERRO ao inicializar Google Cloud TTS: {e}")
                self.tts_engine = None # Desativa em caso de erro

        elif self.tts_engine == "coqui":
            print("⏳ Carregando modelo Coqui TTS (XTTSv2) na memória...")
            if not os.path.exists(settings.COQUI_VOICE_SAMPLE_PATH):
                print(f"❌ ERRO CRÍTICO: Arquivo de amostra de voz '{settings.COQUI_VOICE_SAMPLE_PATH}' não encontrado.")
                self.tts_engine = None
            else:
                try:
                    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=(device == "cuda"))
                    print(f"✅ Modelo Coqui TTS carregado com sucesso no dispositivo '{device}'.")
                except Exception as e:
                    print(f"❌ ERRO ao carregar modelo Coqui TTS: {e}."); traceback.print_exc()
                    self.tts_engine = None

    def transcribe_from_file(self, audio_file_path: str) -> str:
        
        if not self.groq_client: return "Sistema de audição offline."
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()), model="whisper-large-v3", language="pt")
            return transcription.text
        except Exception as e:
            print(f"❌ ERRO ao transcrever com Whisper/Groq: {e}"); traceback.print_exc()
            return None

    def text_to_speech_file(self, text: str) -> str:
        """
        Gera o áudio usando o motor de TTS selecionado na configuração.
        """
        if not self.tts_engine:
            print("   ⚠️ Nenhum motor de TTS está ativo. Impossível gerar voz.")
            return None
        
        print(f"   Gerando áudio com o motor '{self.tts_engine}'...")
        if self.tts_engine == "google":
            return self._tts_google(text)
        elif self.tts_engine == "coqui":
            return self._tts_coqui(text)
        
        return None

    def _tts_google(self, text: str) -> str:
        """Função privada para gerar áudio com Google Cloud TTS."""
        output_filename = "response.mp3"
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="pt-BR",
                name=settings.GOOGLE_TTS_VOICE_NAME
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = self.tts_model.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            with open(output_filename, "wb") as out:
                out.write(response.audio_content)
            return output_filename
        except Exception as e:
            print(f"❌ ERRO no motor Google TTS: {e}"); traceback.print_exc()
            return None

    def _tts_coqui(self, text: str) -> str:
        """Função privada para gerar áudio com Coqui TTS."""
        output_filename = "response.wav"
        try:
            self.tts_model.tts_to_file(
                text=text,
                file_path=output_filename,
                speaker_wav=settings.COQUI_VOICE_SAMPLE_PATH,
                language="pt",
                split_sentences=True
            )
            return output_filename
        except Exception as e:
            print(f"❌ ERRO no motor Coqui TTS: {e}"); traceback.print_exc()
            return None