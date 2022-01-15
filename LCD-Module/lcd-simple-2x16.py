#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep
from Adafruit_CharLCD import Adafruit_CharLCD

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
                       cols=16, lines=2)


def print_display(txt):
     print txt
     lcd.message(txt)



lcd.clear()
sleep(1)
print_display("Hello")
sleep(3)
print_display(' World!')
sleep(3)
print_display("\nSecond line..")
sleep(3)
lcd.clear()
print_display("Bye!")

#lcd.clear()
