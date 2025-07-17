# bmo_core/services/display_manager.py
# Gerencia a tela OLED. Também possui auto-detecção.

# Importa a flag de detecção do gerenciador de hardware
from .hardware_manager import IS_RASPBERRY_PI

if IS_RASPBERRY_PI:
    try:
        import board
        import adafruit_ssd1306
        from PIL import Image, ImageDraw
        CAN_USE_DISPLAY = True
    except ImportError:
        print("⚠️  Aviso: Bibliotecas de display não encontradas na Pi. DisplayManager rodará em modo de simulação.")
        CAN_USE_DISPLAY = False
else:
    CAN_USE_DISPLAY = False


class DisplayManager:
    def __init__(self):
        self.is_active = False
        if CAN_USE_DISPLAY:
            try:
                i2c = board.I2C()
                self.disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
                self.width, self.height = self.disp.width, self.disp.height
                self.image = Image.new("1", (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                self.clear()
                self.is_active = True
                print("✅ DisplayManager real (OLED) inicializado.")
            except (ValueError, RuntimeError) as e:
                print(f"⚠️  Aviso: Display OLED não encontrado ({e}). Rodando em modo de simulação.")
                self.is_active = False
        
        if not self.is_active:
            print("   (DisplayManager em modo de simulação)")

    def _update(self):
        if self.is_active:
            self.disp.image(self.image)
            self.disp.show()

    def draw_face(self, expression="neutral"):
        if self.is_active:
            self.clear()
            # Adicione seu código de desenho de rosto aqui se quiser
            self._update()
        else:
            print(f"[DUMMY DISPLAY] Rosto: {expression}")
    
    def clear(self):
        if self.is_active:
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            self._update()