#!/usr/bin/python
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

pblue  = GPIO.PWM(17, 50)  # frequency=50Hz
pgreen = GPIO.PWM(27, 50)  # frequency=50Hz
pred   = GPIO.PWM(22, 50)  # frequency=50Hz

pred.start(0)
pgreen.start(0)
pblue.start(0)

try:
    while 1:
        for dc in range(0, 101, 5):
            pred.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            pred.ChangeDutyCycle(dc)
            time.sleep(0.1)
        pred.ChangeDutyCycle(80)
        time.sleep(1.0)
        for dc in range(0, 101, 5):
	    pblue.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
	    pblue.ChangeDutyCycle(dc)
            time.sleep(0.1)

except KeyboardInterrupt:
    pass
    pred.stop()
    pblue.stop()
    GPIO.cleanup()
