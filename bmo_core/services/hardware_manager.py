# bmo_core/services/hardware_manager.py
# Gerencia o hardware GPIO (LEDs, etc.). Contém a lógica de auto-detecção.

import time

try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
except (ImportError, RuntimeError):
    IS_RASPBERRY_PI = False

class HardwareManager:
    def __init__(self):
        self.led_pin = 17 
        if IS_RASPBERRY_PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)
            GPIO.setwarnings(False)
            self.led_off()
            print("✅ HardwareManager real (GPIO) inicializado.")
        else:
            print("   (HardwareManager em modo de simulação)")

    def led_on(self):
        if IS_RASPBERRY_PI:
            GPIO.output(self.led_pin, GPIO.HIGH)
        else:
            print("[DUMMY HARDWARE] LED ON")

    def led_off(self):
        if IS_RASPBERRY_PI:
            GPIO.output(self.led_pin, GPIO.LOW)
        else:
            print("[DUMMY HARDWARE] LED OFF")
    
    def cleanup(self):
        if IS_RASPBERRY_PI:
            print("🧹 Limpando pinos GPIO...")
            GPIO.cleanup()