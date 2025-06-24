# bmo_core/audio_manager.py
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
from . import config

class AudioManager:
    def __init__(self, hardware_manager):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.hardware = hardware_manager
        print("Sistema de áudio do BMO pronto.")

    def speak(self, text):
        print(f"BMO: {text}")
        self.hardware.led_on()
        try:
            tts = gTTS(text=text, lang='pt-br')
            tts.save("response.mp3")
            audio = AudioSegment.from_mp3("response.mp3")
            play(audio)
        except Exception as e:
            print(f"Erro ao tentar falar: {e}")
        finally:
            if os.path.exists("response.mp3"):
                os.remove("response.mp3")
            self.hardware.led_off()

    def listen_and_transcribe(self):
        with self.microphone as source:
            print("BMO está ouvindo...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.hardware.led_blink(0.2)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None

        try:
            print("Processando som...")
            self.hardware.led_on()
            text = self.recognizer.recognize_google(audio, language='pt-BR')
            print(f"{config.USER_NAME} disse: {text}")
            return text
        except sr.UnknownValueError:
            self.speak(f"Os circuitos do BMO estão confusos! Não entendi.")
            return None
        except sr.RequestError:
            self.speak("Oh não! A conexão de áudio falhou.")
            return None
        finally:
            self.hardware.led_off()

    def transcribe_from_file(self, audio_file_path):
        """Transcreve áudio a partir de um arquivo."""
        with sr.AudioFile(audio_file_path) as source:
            # O recognizer precisa saber o formato, mas o WAV é bem suportado
            audio_data = self.recognizer.record(source)
        try:
            # Usa a API de reconhecimento de fala do Google
            text = self.recognizer.recognize_google(audio_data, language='pt-BR')
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition não conseguiu entender o áudio")
            return None
        except sr.RequestError as e:
            print(f"Não foi possível solicitar resultados do Google Speech Recognition; {e}")
            return None

    def text_to_speech_file(self, text):
        """Converte texto para um arquivo .mp3 e retorna o nome do arquivo."""
        output_filename = "response.mp3"
        tts = gTTS(text=text, lang='pt-br', slow=False)
        tts.save(output_filename)
        return output_filename