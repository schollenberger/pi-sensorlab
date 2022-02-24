#!/usr/bin/python
#
# Runs on both Python2 and Python3

import RPi.GPIO as GPIO
from time import sleep
from Adafruit_CharLCD import Adafruit_CharLCD

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=25, d7=24,
                       cols=20, lines=4)


def print_display(ln1, ln2="" , ln3='' ,ln4=''):
     lcd.clear()
     if len(ln2) == 0:
          print(' 1 - <{0}>'.format(ln1))
          lcd.message("{0}".format(ln1))
     elif len(ln3) == 0:
          print(' 1 - <{0}>'.format(ln1))
          print(' 2 - <{0}>'.format(ln2))
          lcd.message("{0}\n{1}".format(ln1,ln2))
     else:
          print(' 1 - <{0:20s}>'.format(ln1))
          print(' 2 - <{0:20s}>'.format(ln2))
          print(' 3 - <{0:20s}>'.format(ln3))
          print(' 4 - <{0:20s}>'.format(ln4))
          lcd.message("{0:20s}{2:20s}{1:20s}{3:20s}".format(ln1,ln2,ln3,ln4))
     print("--------------------")


if __name__ == "__main__":
     lcd.clear()
     try:
          sleep(1)
          print_display("Hello")
          sleep(3)
          print_display('Hello World!')
          sleep(3)
          print_display("Hello World", "Second line..")
          sleep(3)
          lcd.clear()
          print_display("Line1","Line2","Line3","Line4")
          sleep(5)
          lcd.clear()
          print_display("Bye!")
          #lcd.clear()
     except KeyboardInterrupt:
          print("\nKeyboard interrupt.")
          print_display("Interrupted....")
