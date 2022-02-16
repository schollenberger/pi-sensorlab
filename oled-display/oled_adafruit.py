#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This module defines the custom OLED dDisplay object based on the
# Adafruit OLED module. It only works with the SSD1306 controller.
#
# It uses the luma.core.reder.canvas object to display text.
#
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image

class OledAdafruit:
    def __init__(self, device,font = None):
        self.device = device
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

     oled_dev = sh1106(i2cdev)
#     oled_dev = ssd1306(i2cdev)

     myfont=ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 15)
     oled = OledLuma(oled_dev, myfont)
     oled.greeting()
     print("Module works correctly if you can see the message 'OLED-Display' on your OLED display.")
     print("Waiting 5 sec before exiting - which should clear the display.")
     sleep(5)
     # Note, deleting the display device doesn't clear the display but exiting the program does.
     print("That's all...")
