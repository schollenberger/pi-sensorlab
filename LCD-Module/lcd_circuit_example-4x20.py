#!/usr/bin/python3
#
# This is a simple demo leveraging the Adafruit Circuit-LCD module
# see: https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/blob/main/examples/charlcd_mono_simpletest.py
# Adafruit Circuit library requires Python3 and Blinka

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd
import lcd_circuit_ports as plcd

from time import sleep

lcd_columns = 20
lcd_rows = 4

lcd = character_lcd.Character_LCD_Mono(plcd.rs, plcd.en, plcd.d4, plcd.d5, plcd.d6, plcd.d7,
         lcd_columns, lcd_rows, plcd.backlight, True)

if __name__ == "__main__":
     sleep_duration = 3
     try:
        lcd.message ="Hello!"
        print(lcd.message)
        sleep(sleep_duration)
        lcd.clear()
        lcd.message="Line1\nLine2\nLine3\nLine4"
        print(lcd.message)
        sleep(sleep_duration)
        lcd.clear()
        # Print two line message right to left
        print("-- From right to left")
        lcd.text_direction = lcd.RIGHT_TO_LEFT
        lcd.message = "Hello\nCircuitPython"
        print(lcd.message)
        sleep(sleep_duration)
        # Return text direction to left to right
        lcd.clear()
        print("-- Back to from right to left")
        lcd.text_direction = lcd.LEFT_TO_RIGHT
        lcd.message = "Hello\nCircuitPython"
        print(lcd.message)
        sleep(sleep_duration)
        # Display cursor
        lcd.clear()
        lcd.cursor = True
        lcd.message = "Cursor on! "
        print(lcd.message)
        sleep(sleep_duration)
        # Display blinking cursor
        lcd.clear()
        lcd.blink = True
        lcd.message = "Blinky Cursor!"
        print(lcd.message)
        sleep(sleep_duration)
        lcd.blink = False
        lcd.cursor = False
        lcd.clear()
        # Create message to scroll
        scroll_msg = "<-- Scroll"
        lcd.message = scroll_msg
        print(lcd.message)
        # Scroll message to the left
        for i in range(len(scroll_msg)):
             sleep(0.5)
             lcd.move_left()
        # Scroll message to the right
        lcd.clear()
        scroll_msg ="Scroll --->"
        lcd.message = scroll_msg
        print(lcd.message)
        for i in range(lcd_columns):
             sleep(0.5)
             lcd.move_right()

        lcd.clear()
        lcd.message = "Going to sleep\nCya later!"
        print(lcd.message)
        sleep(sleep_duration)
        print("Turn backlight off...")
        lcd.backlight = False
        sleep(sleep_duration)
        print("Turn backlight on again...")
        lcd.backlight = True

        # creating a new character - ASCII 0x00
        lcd.clear()
        lcd.message = "New char before: <\x00>"
        print(lcd.message)
        sleep(sleep_duration)
        # 8 rows (bytes) of 5 bits (0x01 - 0x10)
        checkmark = bytes([0x0, 0x0, 0x1, 0x3, 0x16, 0x1C, 0x8, 0x0])

        # Store in LCD character memory 0
        lcd.create_char(0, checkmark)
        lcd.clear()
        lcd.message = "\x00 Success \x00"
        print(lcd.message)
        sleep(sleep_duration)

        lcd.clear()
        lcd.message= "Bye!"
        print(lcd.message)
        #lcd.clear()
        print("That's all...")

     except KeyboardInterrupt:
          print("\nKeyboard interrupt.")
#          lcd.clear()
#          lcd.message = "Interrupted...."

