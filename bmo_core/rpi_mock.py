# bmo_core/rpi_mock.py

# Este módulo simula a biblioteca RPi.GPIO quando o código está
# rodando em uma máquina que não é uma Raspberry Pi

print("****************************************************************")
print("AVISO: Usando a biblioteca RPi.GPIO MOCK para desenvolvimento.")
print("Nenhum pino de hardware real será controlado.")
print("****************************************************************")

BCM = 11
OUT = 1
HIGH = 1
LOW = 0

def setmode(mode):
    print(f"[MOCK] GPIO mode set to BCM")

def setup(channel, mode):
    print(f"[MOCK] Pin {channel} set up as an output pin.")

def output(channel, state):
    status = "HIGH/ON" if state == HIGH else "LOW/OFF"
    print(f"[MOCK] Pin {channel} set to {status}")

def cleanup():
    print("[MOCK] GPIO.cleanup() called. All pins reset.")

def setwarnings(flag):
    print(f"[MOCK] GPIO warnings have been disabled.")