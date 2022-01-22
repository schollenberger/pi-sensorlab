# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Display a custom character"""
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import lcd_circuit_ports as plcd

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2


# Initialise the LCD class
lcd = characterlcd.Character_LCD_Mono(
    plcd.rs, plcd.en, plcd.d4, plcd.d5, plcd.d6, plcd.d7, lcd_columns, lcd_rows
)

checkmark = bytes([0x0, 0x0, 0x1, 0x3, 0x16, 0x1C, 0x8, 0x0])

# Store in LCD character memory 0
lcd.create_char(0, checkmark)

lcd.clear()
lcd.message = "\x00 Success \x00"
