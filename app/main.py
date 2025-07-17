# main.py
# Versão adaptada para rodar em qualquer PC (Windows/Mac/Linux) sem hardware da Pi.

from bmo_core.services.audio_manager import AudioManager
from bmo_core.ai_manager import AIManager
from bmo_core.services.wake_word_detector import WakeWordDetector
from config import settings
import time

# --- Módulos Principais (iniciados como None) ---
hardware = None
audio = None
ai = None
detector = None
display = None 

# --- Classes Falsas (Dummies) para Simular Hardware ---

class DummyHardware:
    """Um gerenciador de hardware falso que apenas imprime ações no console."""
    def __init__(self):
        print("[AVISO] Rodando sem hardware GPIO real. Usando DummyHardware.")
    def led_on(self):
        print("[HARDWARE DUMMY] LED ON")
    def led_off(self):
        print("[HARDWARE DUMMY] LED OFF")
    def led_blink(self, duration=0.5):
        print("[HARDWARE DUMMY] LED BLINK")
    def cleanup(self):
        pass

class DummyDisplay:
    """Um gerenciador de display falso que não faz nada, para evitar crashes."""
    def __init__(self):
        print("[AVISO] Rodando sem display. Usando DummyDisplay.")
    def draw_face(self, expression="neutral"):
        print(f"[DISPLAY DUMMY] Mostrando rosto: {expression}")
    def show_message(self, text):
        print(f"[DISPLAY DUMMY] Mostrando mensagem: {text}")
    def clear(self):
        pass

# --- Lógica Principal do BMO ---

def main_bmo_logic():
    """Esta função é o que acontece DEPOIS que a wake-word é ouvida."""
    display.draw_face("happy") 
    audio.speak(f"Sim, {settings.USER_NAME}?")
    
    display.draw_face("listening")
    user_question = audio.listen_and_transcribe()
    
    if user_question:
        display.draw_face("thinking")
        response = ai.ask(user_question)
        
        display.draw_face("speaking")
        audio.speak(response)
    
    display.draw_face("neutral")
    print(f"\nBMO aguardando comando...")


# --- Ponto de Entrada do Programa ---

if __name__ == "__main__":
    try:
        # 1. Tenta inicializar o hardware real, se falhar, usa os Dummies
        try:
            from bmo_core.services.hardware_manager import HardwareManager
            hardware = HardwareManager()
        except Exception as e:
            print(f"Não foi possível carregar HardwareManager: {e}")
            hardware = DummyHardware()
            
        try:
            from bmo_core.services.display_manager import DisplayManager
            display = DisplayManager()
            if not display.is_active: # Se o módulo carregou mas a tela não foi encontrada
                raise RuntimeError("Display inativo.")
        except Exception as e:
            print(f"Não foi possível carregar DisplayManager: {e}")
            display = DummyDisplay()

        # 2. Inicializa os módulos de software (que dependem dos de hardware)
        ai = AIManager()
        # O AudioManager precisa de um objeto 'hardware', seja ele real ou dummy
        audio = AudioManager(hardware) 
        detector = WakeWordDetector(on_wake_word_callback=main_bmo_logic)

        # 3. Iniciar o processo
        display.draw_face("neutral")
        audio.speak("BMO está online!")
        detector.start()

    except KeyboardInterrupt:
        print("\nDesligando BMO... zzz...")
        if display: display.show_message("Dormindo...")
    except Exception as e:
        print(f"Ocorreu um erro fatal no main: {e}")
        if display: display.show_message("Erro!")
    finally:
        # 4. Limpeza
        if detector: detector.stop()
        if hardware: hardware.cleanup()
        if display: display.clear()