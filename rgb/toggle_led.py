#!/usr/bin/python
import time
import RPi.GPIO as GPIO

chan_list = [22,27,17]  # red, green, blue
col_list = ["red", "green", "blue"]
delay = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(chan_list,  GPIO.OUT)

print ("Rotating RGB LED ...")
GPIO.output(chan_list, GPIO.LOW)

i = 0
try:
    while 1:
         print ("LED color = " + col_list[i])
         GPIO.output(chan_list[i], GPIO.HIGH)
         time.sleep(delay)
         GPIO.output(chan_list[i], GPIO.LOW)
#         time.sleep(delay)
         i = (i + 1) % 3

except KeyboardInterrupt:
    pass
    GPIO.output(chan_list, GPIO.LOW)
    GPIO.cleanup()
