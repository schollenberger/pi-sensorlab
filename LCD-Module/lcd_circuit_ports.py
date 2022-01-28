#!/usr/bin/python3
#
# This module defines the custom lcd GPIO ports

# see: https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/blob/main/examples/charlcd_mono_simpletest.py
# Adafruit Circuit library requires Python3 and Blinka

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

rs = digitalio.DigitalInOut(board.D21)
en = digitalio.DigitalInOut(board.D20)
d7 = digitalio.DigitalInOut(board.D24)
d6 = digitalio.DigitalInOut(board.D25)
d5 = digitalio.DigitalInOut(board.D12)
d4 = digitalio.DigitalInOut(board.D16)
backlight = digitalio.DigitalInOut(board.D23)


if __name__ == "__main__":
     lcd_columns = 20
     lcd_rows = 4

     lcd = character_lcd.Character_LCD_Mono(rs, en, d4, d5, d6, d7, lcd_columns, lcd_rows,
              backlight, True)
     lcd.clear()
     lcd.message = "Hello\nCircuitPython"
     print("Module works correctly if you can see the message 'Hello CircuitPython' on your display.")
