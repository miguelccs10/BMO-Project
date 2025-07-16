# bmo_core/display_manager.py
# (Versão 2.5 - Gerenciamento de Display OLED)

from .hardware_manager import IS_RASPBERRY_PI

if IS_RASPBERRY_PI:
    try:
        import board, adafruit_ssd1306
        from PIL import Image, ImageDraw
    except ImportError:
        IS_RASPBERRY_PI = False # Força modo dummy se libs não estiverem instaladas

class DisplayManager:
    def __init__(self):
        self.is_active = False
        if IS_RASPBERRY_PI:
            try:
                i2c = board.I2C()
                self.disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
                self.width, self.height = self.disp.width, self.disp.height
                self.image = Image.new("1", (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                self.clear()
                self.is_active = True
            except (ValueError, RuntimeError) as e:
                print(f"⚠️  Aviso: Display OLED não encontrado ({e}).")
        
        if not self.is_active: print("   (DisplayManager em modo de simulação)")

    def _update(self):
        if self.is_active: self.disp.image(self.image); self.disp.show()

    def draw_face(self, expression="neutral"):
        if self.is_active:
            self.clear()
            # ... seu código de desenho de rosto aqui ...
            self._update()
        else:
            print(f"[DUMMY] Display: Rosto {expression}")
    
    def clear(self):
        if self.is_active:
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            self._update()