# record_samples.py
import speech_recognition as sr
import os
import time

# --- Configurações ---
WAKE_WORD = "ei_bmo"
OUTPUT_FOLDER = f"training_samples/{WAKE_WORD}"
NUMBER_OF_SAMPLES = 100

def record_audio_sample(sample_number):
    """Grava um único arquivo de áudio e o salva."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ajustando para o ruído do ambiente...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        input(f"\n--- Amostra {sample_number}/{NUMBER_OF_SAMPLES} --- \nPressione Enter e, quando vir 'FALE AGORA', diga 'Ei, BMO' claramente.")
        
        print("FALE AGORA!")
        
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
            filename = os.path.join(OUTPUT_FOLDER, f"sample_{sample_number}.wav")
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            print(f"Salvo em: {filename}")
            return True
        except sr.WaitTimeoutError:
            print("❌ Tempo esgotado. Nenhuma fala detectada. Tente novamente.")
            return False

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("🎙️  Iniciando gravação de amostras para a wake-word 'Ei, BMO'.")
    print("Encontre um local silencioso e fale de forma natural.")

    sample_count = 1
    while sample_count <= NUMBER_OF_SAMPLES:
        if record_audio_sample(sample_count):
            sample_count += 1
        time.sleep(0.5)
        
    print(f"\n✅ Gravação concluída! Você tem {NUMBER_OF_SAMPLES} amostras na pasta '{OUTPUT_FOLDER}'.")