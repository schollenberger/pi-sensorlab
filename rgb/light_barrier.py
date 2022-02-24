#!/usr/bin/python
import time
import RPi.GPIO as GPIO

chan_list = [22,27,17]  # red, green, blue
col_list = ["red", "green", "blue"]
#lbarrier = 18
lbarrier = 23
delay = 0.1

GPIO.setmode(GPIO.BCM)
GPIO.setup(chan_list,  GPIO.OUT)
GPIO.setup(lbarrier, GPIO.IN)

print ("Light barrier - display status via red/green LED ...")
GPIO.output(chan_list, GPIO.LOW)

igreen = 1
ired = 0

GPIO.output(chan_list[igreen], GPIO.HIGH)
state = 0

try:
    while 1:
         barrier = GPIO.input(lbarrier)
#         print ("Light barrier status = ", barrier, "State = ", state)
         if(barrier == 1 and state == 0 ):
		print("Barrier trapped...")
                state = 1
                GPIO.output(chan_list[igreen], GPIO.LOW)
                GPIO.output(chan_list[ired], GPIO.HIGH)
         elif(barrier == 0 and state == 1):
		print("Barrier cleared...")
                state = 0
                GPIO.output(chan_list[ired], GPIO.LOW)
                GPIO.output(chan_list[igreen], GPIO.HIGH)

         time.sleep(delay)

except KeyboardInterrupt:
    pass
    GPIO.output(chan_list, GPIO.LOW)
    GPIO.cleanup()
