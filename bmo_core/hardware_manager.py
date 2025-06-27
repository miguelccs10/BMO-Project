# bmo_core/hardware_manager.py

import time
from . import config

# --- Lógica de Importação Condicional ---
try:
    # Tenta importar a biblioteca real da Raspberry Pi
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
except (ImportError, RuntimeError):
    # Se falhar, estamos em um PC. Importa nosso módulo falso (mock).
    from . import rpi_mock as GPIO
    IS_RASPBERRY_PI = False


class HardwareManager:
    def __init__(self):
        if IS_RASPBERRY_PI:
            print("Hardware real da Raspberry Pi detectado.")
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.LED_PIN, GPIO.OUT)
        GPIO.setwarnings(False)
        self.led_off()

    def led_on(self):
        GPIO.output(config.LED_PIN, GPIO.HIGH)

    def led_off(self):
        GPIO.output(config.LED_PIN, GPIO.LOW)

    def led_blink(self, duration=0.5):
        self.led_on()
        time.sleep(duration)
        self.led_off()

    def cleanup(self):
        print("Limpando recursos do hardware...")
        GPIO.cleanup()