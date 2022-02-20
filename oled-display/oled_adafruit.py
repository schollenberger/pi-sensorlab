#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This module defines the custom OLED dDisplay object based on the
# Adafruit OLED module. It works for the SSD1306 only.
#
# The display stays on after program exit if not cleared manually.
#
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

class OledAdafruit:
    def __init__(self, device, font = None):
        self.device = device
        if not font:
            self.oled_font=ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 10)
        else:
            self.oled_font=font

        self.device.fill(0)
        self.device.show()

    def greeting(self, txt = None):
        if not txt:
            greeting_text = "OLED-Display"
        else:
            greeting_text = txt

        img = Image.new("1", (self.device.width, self.device.height))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0,0,self.device.width-1, self.device.height-1), outline = "white", fill = "black")
        draw.text((10, 10), greeting_text, font = self.oled_font, fill = "white")

        self.device.image(img)
        self.device.show()


    def display_text(self, txt):
        img = Image.new("1", (self.device.width, self.device.height))
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), txt, font = self.oled_font, fill = "white")
        self.device.image(img)
        self.device.show()

    def clear(self):
        self.device.fill(0)
        self.device.show()

    def hide(self):
        self.device.poweroff()

    def show(self):
        self.device.poweron()


if __name__ == "__main__":
     from time import sleep
     i2cdev = busio.I2C(SCL, SDA)
     ada_dev = adafruit_ssd1306.SSD1306_I2C(128, 64, i2cdev)

     myfont=ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 15)
     oled = OledAdafruit(ada_dev, myfont)
     oled.greeting()
     print("Module works correctly if you can see the message 'OLED-Display' on your OLED display.")
     print("Waiting 5 sec before hiding the display...")
     sleep(5)
     print("...hide...")
     oled.hide()
     print("Waiting 5 sec before showing the display again ...")
     sleep(5)
     print("...show...")
     oled.show()
     print("Waiting 5 sec and then clear the display for 5 sec...")
     sleep(5)
     print("Clear...")
     oled.clear()
     sleep(5)
     print("Greeting...")
     oled.greeting()
     print("Waiting 5 sec before clearing the display and exiting.")
     sleep(5)
     oled.clear()
     print("That's all...")
