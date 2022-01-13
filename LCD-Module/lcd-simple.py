#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep
from Adafruit_CharLCD import Adafruit_CharLCD

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
                       cols=16, lines=2)

lcd.message('Hello')
sleep(3)
lcd.message('Hello')
lcd.clear()
