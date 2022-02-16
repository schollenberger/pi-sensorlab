#! /usr/bin/python3
# -*- coding: utf-8 -*-
# derived from:
#   https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

from time import sleep
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

print("Clear display...")
# Clear display.
disp.fill(0)
disp.show()
print ("Wait 1 sec...")
sleep(1)


# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
print("Dislplay dimensions: {0:d} x {1:d}".format(width, height))

image = Image.new("1", (width, height))


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
print("Draw black box with text ...")

oled_font = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 14)
draw.rectangle((0, 0, width-1, height-1), outline=255, fill=0)
draw.text((5, 5), "OLED-Display", font=oled_font, fill=255)
draw.text((5, 20), "SSD1360", font=oled_font, fill=255)


disp.image(image)
disp.show()

print ("Wait 5 sec...")
sleep (5)

# Draw a white filled box.
print("Draw white box ...")

draw.rectangle((0, 0, width, height), outline=255, fill=255)

disp.image(image)
disp.show()

print ("Wait 1 sec...")
sleep (1)


# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
y = top
fh = 9

# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

print("Some text...")
draw.rectangle((0, 0, width, height), outline=0, fill=0)
draw.text((x, y), "A234567890B23456789C", font=font, fill=255)
y = y + fh + padding
draw.text((x, y), "abcdefghijklmnopqrstuvwxyz", font=font, fill=255)
y = y + fh + padding
draw.text((x, y), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=font, fill=255)
y = y + fh + padding
draw.text((x, y), "!§$%&/()?,.-_:;#+*", font=font, fill=255)
y = y + fh + padding

disp.image(image)
disp.show()

print ("Wait 10 sec...")
sleep (10)

disp.fill(0)
disp.show()

print ("Done...")
