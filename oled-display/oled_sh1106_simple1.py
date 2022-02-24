#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Basic examples using the luma.oled library.

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from time import sleep

# Initialize OLED I2C display device

serial = i2c(port=1, address=0x3C)
#device = sh1106(serial)
device = ssd1306(serial)

# Get a nice font

#oled_font = ImageFont.truetype('FreeSans.ttf', 14)
oled_font = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 14)

# Use the luma.core canvas to draw onto the display

print("Draw black filled rectangle and write OLED-Display in 14pt SansMono font...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline = "white", fill = "black")
    draw.text((10, 10), "OLED-Display", font = oled_font, fill = "white")
#    draw.text((10, 10), "OLED-Display", fill = "white")

sleep(3)

# Code example without transaction context - can be used on a Python interpreter shell nicely

print("Clear the text - rectangle only...")

_can = canvas(device)
draw = _can.__enter__()
_box = device.bounding_box
print("Bounding box:", _box)
draw.rectangle(_box, outline = "white", fill = "black")
_can.__exit__(None,None,None)

sleep(3)

print("Draw white filled rectangle and write OLED-Display in black with default font...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline = "white", fill = "white")
    draw.text((10, 10), "OLED-Display", fill = "black")

sleep(3)

print("Display off...")
device.hide()
sleep(3)

print("And Display on again...")
device.show()
sleep(3)


print("That's all...")
