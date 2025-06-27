# bmo_core/display_manager.py

import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

class DisplayManager:
    def __init__(self):
        self.is_active = False
        try:
            # Tenta inicializar a comunicação I2C e a tela
            i2c = board.I2C()
            self.disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
            self.width = self.disp.width
            self.height = self.disp.height
            
            self.image = Image.new("1", (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
            
            self.clear()
            print("Display OLED inicializado com sucesso.")
            self.is_active = True
        except (ValueError, RuntimeError, AttributeError) as e:
            print(f"AVISO: Não foi possível inicializar o display OLED. {e}")
            print("O programa continuará sem suporte a display.")

    def _update_display(self):
        if not self.is_active: return
        self.disp.image(self.image)
        self.disp.show()

    def clear(self):
        if not self.is_active: return
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self._update_display()
        
    def draw_face(self, expression="neutral"):
        if not self.is_active: return
        self.clear()
        
        eye_y = 25
        if expression == "listening":
            self.draw.rectangle((34, eye_y-5, 54, eye_y+15), outline=255, fill=255)
            self.draw.rectangle((74, eye_y-5, 94, eye_y+15), outline=255, fill=255)
        elif expression == "thinking":
            self.draw.line((34, eye_y+5, 54, eye_y+5), fill=255, width=4)
            self.draw.line((74, eye_y+5, 94, eye_y+5), fill=255, width=4)
        else:
            self.draw.rectangle((38, eye_y, 52, eye_y+10), outline=255, fill=0)
            self.draw.rectangle((76, eye_y, 90, eye_y+10), outline=255, fill=0)

        mouth_y = 48
        if expression == "speaking":
            self.draw.rectangle((54, mouth_y-5, 74, mouth_y+5), outline=255, fill=0)
        elif expression == "happy":
            self.draw.arc((45, mouth_y-10, 83, mouth_y+5), 0, 180, fill=255, width=2)
        else:
            self.draw.line((50, mouth_y, 78, mouth_y), fill=255, width=2)
        
        self._update_display()