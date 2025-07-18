# bmo.py
# Ponto de entrada final para o BMO autônomo.
# Implementa a lógica de memória persistente por execução ("Alexa-like").

print("--- Iniciando Sistemas do BMO ---")

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

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

# --- Configurações ---
WAKE_WORD_MODEL_PATH = "custom_models/wake_word/ei_bmo.onnx"
RECORDING_PATH = "temp_question.wav"
CHUNK = 1280
RATE = 16000
RECORD_SECONDS = 5
WAKE_WORD_THRESHOLD = 0.985

# --- Inicialização dos Módulos ---
hardware = HardwareManager()
display = DisplayManager()
audio_manager = AudioManager(hardware)
bmo_agent = BMOAgent()

# --- ID de Sessão Persistente para esta Execução ---
# Criamos um único ID quando o programa inicia e o reutilizamos.
BMO_SESSION_ID = f"bmo-session-{str(uuid.uuid4())}"
print(f"✅ Sessão de memória iniciada com o ID: ...{BMO_SESSION_ID[-12:]}")


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
    with wave.open(RECORDING_PATH, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio_interface.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    return RECORDING_PATH

def play_response(audio_file_path, stream):
    if not audio_file_path or not os.path.exists(audio_file_path): return
    
    # Pausa a detecção de wake-word para evitar que o BMO se ouça
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
        # Reativa a detecção de wake-word após a fala
        stream.start_stream()
        print("   (Detecção de wake-word reativada)")


def conversation_cycle(audio_stream, audio_interface):
    """
    Ciclo de conversação que usa a sessão de memória persistente da execução.
    """
    print(f"\n💡 BMO Ativado! (Usando sessão: ...{BMO_SESSION_ID[-12:]})")
    
    question_audio_path = record_question(audio_stream, audio_interface)
    
    user_question = audio_manager.transcribe_from_file(question_audio_path)
    if not user_question:
        ai_response = bmo_agent.run("O áudio estava vazio ou não foi entendido.", session_id=BMO_SESSION_ID)
        response_audio_path = audio_manager.text_to_speech_file(ai_response)
        play_response(response_audio_path, audio_stream)
        return

    print(f"🧠 Processando: '{user_question}'")
    # Passamos o MESMO ID de sessão para o agente a cada chamada.
    ai_response = bmo_agent.run(user_question, session_id=BMO_SESSION_ID)
    print(f"🤖 BMO Respondeu: '{ai_response}'")
    
    response_audio_path = audio_manager.text_to_speech_file(ai_response)
    play_response(response_audio_path, audio_stream)
    
    hardware.led_off(); display.draw_face("neutral")

# --- Loop Principal ---
if __name__ == "__main__":
    if not os.path.exists(WAKE_WORD_MODEL_PATH):
        print(f"❌ ERRO CRÍTICO: Modelo de Wake-Word não encontrado em '{WAKE_WORD_MODEL_PATH}'"); sys.exit(1)

    print("🎤 Verificando e baixando modelos base do OpenWakeWord (se necessário)...")
    # Model.download_and_verify_models() # Removido em favor do script setup_oww.py

    print("⏳ Carregando modelo OpenWakeWord...")
    oww_model = Model(wakeword_models=[WAKE_WORD_MODEL_PATH])
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(rate=RATE, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=CHUNK)
    
    print("\n✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...")
    display.draw_face("neutral"); hardware.led_off()

    try:
        while True:
            audio_chunk = audio_stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            prediction = oww_model.predict(audio_array)
            model_name = os.path.basename(WAKE_WORD_MODEL_PATH).replace(".onnx", "")
            
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
        audio_stream.close(); pa.terminate(); hardware.cleanup()