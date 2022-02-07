#! /usr/bin/python3
# -*- coding: utf-8 -*-

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from time import sleep

# Nun können wir schon unser OLED-Display initialisieren. Das erledigt dieser Code:

i2cdev = i2c(port=1, address=0x3C)
device = sh1106(i2cdev)

#oled_font = ImageFont.truetype('FreeSans.ttf', 14)
oled_font = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 14)
oled_font2 = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 10)

delay = 3

print("White frame with 14pt text...")
with canvas(device) as draw:

    draw.rectangle(device.bounding_box, outline = "white", fill = "black")
    draw.text((10, 10), "OLED-Display", font = oled_font, fill = "white")

sleep(delay)

print("White frame with 10pt text")
with canvas(device) as draw:

    y_first = 10
    font_height = 10
    draw.rectangle(device.bounding_box, outline = "white", fill = "black")
    y_now = y_first
    draw.text((10, y_now), "OLED-Display", font = oled_font2, fill = "white")
    y_now = y_now + font_height + 2
    draw.text((10, y_now), "2nd. Line", font = oled_font2, fill = "white")
    y_now = y_now + font_height + 2
    draw.text((10, y_now), "3rd. Line\nWith new line", font = oled_font2, fill = "white")

#    draw.text((10, 10), "OLED-Display", fill = "white")

sleep(delay)

print("New Frame with black fill - empty...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline = "white", fill = "black")

sleep(delay)

print("White filled frame with standard font black text ...")
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline = "white", fill = "white")
    draw.text((10, 10), "OLED-Display", fill = "black")

sleep(delay)

print("That's all...")
