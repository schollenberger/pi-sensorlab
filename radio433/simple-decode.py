#!/usr/bin/python2
#-----------------------------------------#
# Name - simple-read.py
# Description - This code is to do a simple decode of
#               some 433 Mhz sender by reading  status changes 
#               from an GPIO input.
#               It relays the input status to the ledpin
#               In order to ignore noise, it starts to print out
#               status changes after a signal stays constant for 
#               some milliseconds. Then it tries to skip a preamble
#               burst.
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
#   GPIO.output(ledpin, outval)  # invert LED as sensor is active low
   GPIO.output(ledpin, value)   # non-invertted LED output


def ispreambel(value, duration):
    res = False
    if(value == 0 and duration.total_seconds() > 0.0005 and duration.total_seconds() < 0.0007):
       res = True
       print('Yes1')
    elif(value == 1 and duration.total_seconds() > 0.0001 and duration.total_seconds() < 0.0003):
       res = True
       print('Yes2')
    else:
       print('no')

    return res


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
              if(preambel):
#                 print('..in preambel check')
                 if(ispreambel(preData, duration)):
                    preambelCount = preambelCount + 1
                 else:
                    print('Preamble finished after {0} periods'.format(preambelCount))
                    print('postamble state: {0} - for {1} seconds'.format(preData, duration.total_seconds()))
                    preambelCount = 0
                    preambel = False
                    count = count -1
              else:
                 print('state: {0} - for {1} seconds'.format(preData, duration.total_seconds()))
                 count = count -1
                 if ispreambel(preData, duration):
                     print ('State qualifies as preamble, starting check')
                     preambel = True

           elif(count == 0):
              print('Sequence finished')
              count = -1
           elif(duration.total_seconds() > 0.004):
                 count = 20
                 print('Start sequence with state {0} - for {1} seconds'.format(preData, duration.total_seconds()))
                 print('Checking for preample sequence')
                 _pre = ispreambel(preData, duration)
		 print _pre
		 if(_pre == True):
                    print('...found')
                    preambel = True

	   startTime = endTime
           preData = inData
#           time.sleep(delay)
#        time.sleep(shortDelay)

except KeyboardInterrupt:
    pass
    print("*** KeyboardInterrupt caught ***")
    GPIO.output(ledpin, GPIO.LOW)
    GPIO.cleanup()

