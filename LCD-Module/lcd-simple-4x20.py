#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep
from Adafruit_CharLCD import Adafruit_CharLCD

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
                       cols=20, lines=4)


def print_display(ln1, ln2="" , ln3='' ,ln4=''):
     print(' 1 - <{0:20s}>'.format(ln1))
     if len(ln2) > 0:
          print(' 2 - <{0:20s}>'.format(ln2))
     if len(ln3) > 0:
          print(' 3 - <{0:20s}>'.format(ln3))
     if len(ln3) > 0:
          print(' 4 - <{0:20s}>'.format(ln4))
     print("--------------------")
     lcd.clear()
     if len(ln2) == 0:
          lcd.message("{0:20s}".format(ln1))
     elif len(ln3) == 0:
          lcd.message("{0:20s}\n{1:20s}".format(ln1,ln2))
     else:
          lcd.message("{0:20s}{2:20s}{1:20s}{3:20s}".format(ln1,ln2,ln3,ln4))



lcd.clear()
sleep(1)
print_display("Hello")
sleep(3)
print_display(' World!')
sleep(3)
print_display("\nSecond line..")
sleep(3)
#print_display("4567890Third line 234567890")
lcd.clear()
print_display("Line1","Line2","Line3","Line4")
sleep(10)
lcd.clear()
print_display("Bye!")

#lcd.clear()
