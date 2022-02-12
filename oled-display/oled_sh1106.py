#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This module defines the custom OLED SH1106 Display object compatible to
# a SSD1306 Display and LCD device.
# It is based on the LUMA OLED library.
#
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image

class OledSh1106:
    def __init__(self, i2cbus,font = None):
        self.device = sh1106(i2cbus)
        if not font:
            self.oled_font=ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 10)
        else:
            self.oled_font=font

    def greeting(self):
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline = "white", fill = "black")
            draw.text((10, 10), "OLED-Display", font = self.oled_font, fill = "white")

    def display_text(self, txt):
        with canvas(self.device) as draw:
#            draw.rectangle(self.device.bounding_box, outline = "white", fill = "black")
            draw.text((5, 5), txt, font = self.oled_font, fill = "white")


if __name__ == "__main__":
     from time import sleep

     i2cdev = i2c(port=1, address=0x3C)
     myfont=ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 15)
     lcd = OledSh1106(i2cdev, myfont)
     lcd.greeting()
     print("Module works correctly if you can see the message 'OLED-Display' on your OLED display.")
     print("Waiting 5 sec before closing - which should clear the display.")
     sleep(5)

