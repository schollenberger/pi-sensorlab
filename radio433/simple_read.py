#!/usr/bin/python2
#-----------------------------------------#
# Name - simple-read.py
# Description - This code is to read status changes from an GPIO input.
#               It relays the input status to the ledpin
#               It ignores noise on the pin and starts with a number of
#               probes after the signal has been stable for some 
#               milliseconds (initial burst that starts all)
#
# Author - Werner Schollenberger
#
# Licence - Compleatly Free
# Date - 2021-08-29
#------------------------------------------------------------#
# It doesn't run under python3

#Imports modules
import time
import RPi.GPIO as GPIO
from datetime import datetime

#Static program vars
pin = 11     # GPIO 17 Input - sensor out (GPIO.BOARD)
ledpin = 13  # GPIO 27 Output - LED Green (GPIO.BOARD)

#Sets up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN)
GPIO.setup(ledpin, GPIO.OUT)

def setLed(value):
	outval = [GPIO.HIGH, GPIO.LOW][value]
#	GPIO.output(ledpin, outval)  # invert LED as sensor is active low
	GPIO.output(ledpin, value)   # non-invertted LED output


# Initial values

shortDelay = 0.0
delay = 0.0
count = -1
preambel = False
preambelCount = 0

preData=GPIO.input(pin)
startTime = datetime.now()
setLed(preData)
print('Initial state: {0}'.format(preData))

try:
    while True:
        inData = GPIO.input(pin)
        if(inData != preData):
           endTime = datetime.now()
           duration = endTime  - startTime
           setLed(inData)
           if(count > 0):
               print('state: {0} - for {1} seconds'.format(preData, duration.total_seconds()))
               count = count -1
           elif(count == 0):
              print('Sequence finished')
              count = -1
           elif(duration.total_seconds() > 0.004):
                 count = 20
                 print('Start sequence with state {0} - for {1} seconds'.format(preData, duration.total_seconds()))

	   startTime = endTime
           preData = inData
#           time.sleep(delay)
#        time.sleep(shortDelay)

except KeyboardInterrupt:
    pass
    print("*** KeyboardInterrupt caught ***")
    GPIO.output(ledpin, GPIO.LOW)
    GPIO.cleanup()

