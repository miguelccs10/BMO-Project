# bmo.py
# Ponto de entrada final e autônomo para o BMO.
# Versão com pathlib para compatibilidade de SO, reset de estado do OpenWakeWord,
# e gerenciamento de memória.

import os
import sys
from pathlib import Path

# --- DEFINIÇÃO DE CAMINHOS E CREDENCIAIS (Método Robusto) ---
# Define a raiz do projeto de forma segura para qualquer SO.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define o caminho para as credenciais do Google ANTES de qualquer import do projeto.
credentials_path = BASE_DIR / "google_adc_credentials.json"
if os.path.exists(credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
else:
    print(f"⚠️  AVISO: Arquivo de credenciais '{credentials_path}' não encontrado. APIs do Google podem falhar.")

print("--- Iniciando Sistemas do BMO ---")
sys.path.append(str(BASE_DIR))

import pyaudio
import numpy as np
import wave
import uuid
from openwakeword.model import Model
from pydub import AudioSegment
from pydub.playback import play

print("✅ Carregando cérebro, serviços e ferramentas do BMO...")
from bmo_core.agent.agent_executor import BMOAgent
from bmo_core.services.audio_manager import AudioManager
from bmo_core.services.hardware_manager import HardwareManager
from bmo_core.services.display_manager import DisplayManager

# --- Configurações (usando pathlib) ---
WAKE_WORD_MODEL_PATH = BASE_DIR / "custom_models" / "wake_word" / "ei_bmo.onnx"
RECORDING_PATH = BASE_DIR / "temp_question.wav"
CHUNK = 1280
RATE = 16000
RECORD_SECONDS = 5
WAKE_WORD_THRESHOLD = 0.5
INPUT_DEVICE_INDEX = None # Deixe None para usar o padrão, ou especifique o ID do microfone

# --- Inicialização dos Módulos ---
hardware = HardwareManager()
display = DisplayManager()
audio_manager = AudioManager(hardware)
bmo_agent = BMOAgent()

# --- ID de Sessão Persistente para esta Execução ---
BMO_SESSION_ID = f"bmo-session-{str(uuid.uuid4())}"
print(f"✅ Sessão de memória iniciada com o ID: ...{BMO_SESSION_ID[-12:]}")


# --- Funções Auxiliares ---
def clear_audio_buffer(stream, clear_duration_ms=500):
    """Lê e descarta dados do buffer de áudio para limpar ecos."""
    frames_to_clear = int(RATE / CHUNK * (clear_duration_ms / 1000.0))
    print(f"   Limpando ~{clear_duration_ms}ms de áudio do buffer...")
    for _ in range(frames_to_clear):
        try:
            stream.read(CHUNK, exception_on_overflow=False)
        except IOError:
            pass

# --- Funções do Ciclo de Conversa ---
def record_question(stream, audio_interface):
    print("🎤 Ouvindo sua pergunta...")
    display.draw_face("listening"); hardware.led_on()
    frames = []
    stream.read(CHUNK * 4, exception_on_overflow=False) 
    print(f"   (Gravando por {RECORD_SECONDS} segundos...)")
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    print("✅ Gravação concluída.")
    display.draw_face("thinking")
    with wave.open(str(RECORDING_PATH), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio_interface.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    return str(RECORDING_PATH)

def play_response(audio_file_path, stream):
    if not audio_file_path or not os.path.exists(audio_file_path): return
    
    stream.stop_stream()
    print("   (Detecção de wake-word pausada)")
    print("🔊 Reproduzindo resposta...")
    display.draw_face("speaking")
    try:
        sound = AudioSegment.from_file(audio_file_path)
        play(sound)
    except Exception as e:
        print(f"❌ Erro ao reproduzir o áudio: {e}")
    finally:
        if os.path.exists(audio_file_path): os.remove(audio_file_path)
        stream.start_stream()
        print("   (Detecção de wake-word reativada)")
        clear_audio_buffer(stream)

def conversation_cycle(audio_stream, audio_interface):
    print(f"\n💡 BMO Ativado! (Usando sessão: ...{BMO_SESSION_ID[-12:]})")
    question_audio_path = record_question(audio_stream, audio_interface)
    user_question = audio_manager.transcribe_from_file(question_audio_path)
    if not user_question:
        ai_response = bmo_agent.run("O áudio estava vazio ou não foi entendido.", session_id=BMO_SESSION_ID)
        response_audio_path = audio_manager.text_to_speech_file(ai_response)
        play_response(response_audio_path, audio_stream)
        return

    print(f"🧠 Processando: '{user_question}'")
    ai_response = bmo_agent.run(user_question, session_id=BMO_SESSION_ID)
    print(f"🤖 BMO Respondeu: '{ai_response}'")
    
    response_audio_path = audio_manager.text_to_speech_file(ai_response)
    play_response(response_audio_path, audio_stream)
    
    hardware.led_off(); display.draw_face("neutral")

# --- Loop Principal ---
if __name__ == "__main__":
    if not os.path.exists(WAKE_WORD_MODEL_PATH):
        print(f"❌ ERRO CRÍTICO: Modelo de Wake-Word não encontrado em '{WAKE_WORD_MODEL_PATH}'"); sys.exit(1)

    print("⏳ Carregando modelo OpenWakeWord...")
    oww_model = Model(wakeword_models=[str(WAKE_WORD_MODEL_PATH)])
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=RATE, 
        channels=1, 
        format=pyaudio.paInt16, 
        input=True, 
        frames_per_buffer=CHUNK,
        input_device_index=INPUT_DEVICE_INDEX
    )
    
    print("\n✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...")
    display.draw_face("neutral"); hardware.led_off()

    try:
        while True:
            audio_chunk = audio_stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            prediction = oww_model.predict(audio_array)
            model_name = WAKE_WORD_MODEL_PATH.stem
            
            score = prediction.get(model_name, 0)
            print(f"🎤 Escutando... Confiança: {score:.2f}", end="\r")

            if score > WAKE_WORD_THRESHOLD:
                print(" " * 40, end="\r") 
                conversation_cycle(audio_stream, pa)
                print("   Resetando estado do detector de wake-word...")
                oww_model.reset()
                print("\n✅ BMO voltando a escutar pela wake-word...")
    except KeyboardInterrupt:
        print("\n👋 Desligando BMO...")
    finally:
        print("🧹 Limpando recursos de áudio...")
        audio_stream.close(); pa.terminate()
        if 'hardware' in globals() and hasattr(hardware, 'cleanup'):
            hardware.cleanup()