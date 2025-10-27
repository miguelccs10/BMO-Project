"""
BMO.py
Autonomous voice assistant with wake-word detection.
Refactored to use YAML-based configuration following best practices.
"""

import os
import sys
from pathlib import Path
import uuid
import traceback
import pyaudio
import numpy as np
from openwakeword.model import Model
from pydub import AudioSegment
from pydub.playback import play

# --- Setup paths and credentials before imports ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load configuration early
from config.config_manager import get_config

config = get_config()

# Setup Google credentials
credentials_path = config.BASE_DIR / config.config.google_cloud.adc_credentials_file
if credentials_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
else:
    print(f"⚠️  AVISO: Arquivo de credenciais '{credentials_path}' não encontrado. APIs do Google podem falhar.")

print("--- Iniciando Sistemas do BMO ---")

# Import BMO modules
print("✅ Carregando cérebro, serviços e ferramentas do BMO...")
from bmo_core.agent.agent_executor import BMOAgent
from bmo_core.services.audio_manager import AudioManager
from bmo_core.services.hardware_manager import HardwareManager
from bmo_core.services.display_manager import DisplayManager

# --- Configuration from YAML ---
WAKE_WORD_MODEL_PATH = config.get_wake_word_model_path()
RECORDING_PATH = config.get_path('temp_audio')

# Audio settings
CHUNK = config.config.wake_word.audio.chunk_size
RATE = config.config.wake_word.audio.sample_rate
RECORD_SECONDS = config.config.recording.duration_seconds
WAKE_WORD_THRESHOLD = config.config.wake_word.threshold
INPUT_DEVICE_INDEX = config.config.recording.input_device_index
BUFFER_CLEAR_MS = config.config.recording.buffer_clear_duration_ms

# --- Initialize Modules ---
hardware = HardwareManager()
display = DisplayManager()
audio_manager = AudioManager(hardware)
bmo_agent = BMOAgent()

# --- Persistent Session ID ---
BMO_SESSION_ID = f"bmo-session-{str(uuid.uuid4())}"
print(f"✅ Sessão de memória iniciada com o ID: ...{BMO_SESSION_ID[-12:]}")


def clear_audio_buffer(stream, clear_duration_ms: int = None):
    """Clear audio buffer to prevent echo/false triggers."""
    if clear_duration_ms is None:
        clear_duration_ms = BUFFER_CLEAR_MS

    frames_to_clear = int(RATE / CHUNK * (clear_duration_ms / 1000.0))
    print(f"   Limpando ~{clear_duration_ms}ms de áudio do buffer...")
    for _ in range(frames_to_clear):
        try:
            stream.read(CHUNK, exception_on_overflow=False)
        except IOError:
            pass


def record_question_vad(stream, audio_interface):
    """Record user question using VAD after wake-word detection."""
    print("🎤 Ouvindo sua pergunta...")
    display.draw_face("listening")
    hardware.led_on()

    # Use AudioManager's VAD-based recording
    audio_path, duration = audio_manager.record_with_vad(stream, audio_interface, clear_buffer=True)

    if audio_path:
        print("✅ Gravação concluída.")
        display.draw_face("thinking")
        return audio_path
    else:
        print("⚠️  Nenhum áudio capturado.")
        display.draw_face("neutral")
        return None


def play_response(audio_file_path, stream, audio_interface):
    """Play TTS response and manage stream state."""
    if not audio_file_path or not os.path.exists(audio_file_path):
        return

    stream.stop_stream()
    print("   (Detecção de wake-word pausada)")
    print("🔊 Reproduzindo resposta...")
    display.draw_face("speaking")

    try:
        # Check if output device is configured
        output_device = config.config.recording.output_device_index

        if output_device is not None:
            # Use configured output device with PyAudio
            sound = AudioSegment.from_file(audio_file_path)

            # Export to raw audio for PyAudio playback
            raw_data = sound.raw_data
            sample_rate = sound.frame_rate
            channels = sound.channels
            sample_width = sound.sample_width

            # Create output stream with specified device
            output_stream = audio_interface.open(
                format=audio_interface.get_format_from_width(sample_width),
                channels=channels,
                rate=sample_rate,
                output=True,
                output_device_index=output_device
            )

            # Play audio
            chunk_size = 1024
            for i in range(0, len(raw_data), chunk_size):
                output_stream.write(raw_data[i:i+chunk_size])

            output_stream.stop_stream()
            output_stream.close()
        else:
            # Use default output (pydub's play)
            sound = AudioSegment.from_file(audio_file_path)
            play(sound)

    except Exception as e:
        print(f"❌ Erro ao reproduzir o áudio: {e}")
        traceback.print_exc()
    finally:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        stream.start_stream()
        print("   (Detecção de wake-word reativada)")
        clear_audio_buffer(stream)


def conversation_cycle(audio_stream, audio_interface):
    """Handle one complete conversation cycle."""
    print(f"\n💡 BMO Ativado! (Usando sessão: ...{BMO_SESSION_ID[-12:]})")

    # Record question using VAD
    question_audio_path = record_question_vad(audio_stream, audio_interface)

    if not question_audio_path:
        # No audio captured
        print("   Nenhuma pergunta detectada. Voltando a escutar...")
        hardware.led_off()
        display.draw_face("neutral")
        return

    # Transcribe
    user_question = audio_manager.transcribe_from_file(question_audio_path)

    if not user_question:
        # Handle empty audio
        ai_response = bmo_agent.run(
            config.prompts.errors["audio_empty"],
            session_id=BMO_SESSION_ID
        )
        response_audio_path = audio_manager.text_to_speech_file(ai_response)
        play_response(response_audio_path, audio_stream, audio_interface)
        return

    # Process with agent
    print(f"🧠 Processando: '{user_question}'")
    ai_response = bmo_agent.run(user_question, session_id=BMO_SESSION_ID)
    print(f"🤖 BMO Respondeu: '{ai_response}'")

    # Generate and play response
    response_audio_path = audio_manager.text_to_speech_file(ai_response)
    play_response(response_audio_path, audio_stream, pa)

    hardware.led_off()
    display.draw_face("neutral")


def main():
    """Main loop for wake-word detection and conversation."""
    # Verify wake-word model exists
    if not WAKE_WORD_MODEL_PATH.exists():
        print(f"❌ ERRO CRÍTICO: Modelo de Wake-Word não encontrado em '{WAKE_WORD_MODEL_PATH}'")
        sys.exit(1)

    # Load wake-word model
    print("⏳ Carregando modelo OpenWakeWord...")
    oww_model = Model(
        wakeword_models=[str(WAKE_WORD_MODEL_PATH)],
        inference_framework=config.config.wake_word.inference_framework
    )

    # Setup audio stream
    pa = pyaudio.PyAudio()

    # Display audio device info
    if INPUT_DEVICE_INDEX is not None:
        input_info = pa.get_device_info_by_index(INPUT_DEVICE_INDEX)
        print(f"🎤 Dispositivo de entrada: [{INPUT_DEVICE_INDEX}] {input_info['name']}")
    else:
        print(f"🎤 Dispositivo de entrada: [default]")

    output_device = config.config.recording.output_device_index
    if output_device is not None:
        output_info = pa.get_device_info_by_index(output_device)
        print(f"🔊 Dispositivo de saída: [{output_device}] {output_info['name']}")
    else:
        print(f"🔊 Dispositivo de saída: [default]")

    audio_stream = pa.open(
        rate=RATE,
        channels=config.config.wake_word.audio.channels,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=INPUT_DEVICE_INDEX
    )

    print(f"\n✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...")
    print(f"   (Threshold: {WAKE_WORD_THRESHOLD})")
    display.draw_face("neutral")
    hardware.led_off()

    try:
        while True:
            # Read audio chunk
            audio_chunk = audio_stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)

            # Predict wake-word
            prediction = oww_model.predict(audio_array)
            model_name = WAKE_WORD_MODEL_PATH.stem
            score = prediction.get(model_name, 0)

            print(f"🎤 Escutando... Confiança: {score:.2f}", end="\r")

            # Check if wake-word detected
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
        audio_stream.close()
        pa.terminate()
        if hasattr(hardware, 'cleanup'):
            hardware.cleanup()


if __name__ == "__main__":
    main()
