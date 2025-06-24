# bmo_core/audio_manager.py
import speech_recognition as sr
from gtts import gTTS

class AudioManager:
    def __init__(self, hardware_manager):
        self.recognizer = sr.Recognizer()
        # O hardware_manager é um dummy, mas o mantemos para a estrutura
        self.hardware = hardware_manager 
        print("Sistema de áudio (baseado em arquivos) pronto.")

    def transcribe_from_file(self, audio_file_path):
        """Transcreve áudio a partir de um arquivo."""
        with sr.AudioFile(audio_file_path) as source:
            audio_data = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio_data, language='pt-BR')
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition não conseguiu entender o áudio.")
            return None
        except sr.RequestError as e:
            print(f"Erro no serviço do Google; {e}")
            return None

    def text_to_speech_file(self, text):
        """Converte texto para um arquivo .mp3 e retorna o nome do arquivo."""
        output_filename = "response.mp3"
        try:
            tts = gTTS(text=text, lang='pt-br', slow=False)
            tts.save(output_filename)
            return output_filename
        except Exception as e:
            print(f"Erro ao gerar áudio com gTTS: {e}")
            return None