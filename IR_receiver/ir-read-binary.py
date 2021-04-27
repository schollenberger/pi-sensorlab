#-----------------------------------------#
#Name - IR-Finalised.py
#Description - The finalised code to read data from an IR sensor and then refernce it with stored values
#Author - Lime Parallelogram
#Licence - Compleatly Free
#Date - 12/09/2019
#------------------------------------------------------------#
#Imports modules
import time
import RPi.GPIO as GPIO
from datetime import datetime

#Static program vars
pin = 18 #Input pin of sensor (GPIO.BOARD)
ledpin = 11
#Buttons = [0x300ff9867L, 0x300ffd827L, 0x300ff8877L, 0x300ffa857L, 0x300ffe817L, 0x300ff48b7L, 0x300ff6897L, 0x300ff02fdL, 0x300ff32cdL, 0x300ff20dfL] #HEX code list
#ButtonsNames = ["RED",   "GREEN",      "BLUE",       "WHITE",      "DARK ORANGE","LIGHT GREEN","DARK BLUE",  "VIBRANT ORANGE","LIGHT BLUE","DARK PURPLE"] #String list in same order as HEX list

#Sets up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN)
GPIO.setup(ledpin, GPIO.OUT)

def setLed(value):
	outval = [GPIO.HIGH, GPIO.LOW][value]
	GPIO.output(ledpin, outval)  # invert LED as sensor is active low

#Gets binary value
def getBinary():
	#Internal vars
	num1s = 0 #Number of consecutive 1s read
	binary = 1 #The bianry value
	command = [] #The list to store pulse times in
	previousValue = 0 #The last value
	value = GPIO.input(pin) #The current value
	setLed(value)
	print('Initial sensor value: {0}.'.format(value))
	#Waits for the sensor to pull pin low
	while value:
		value = GPIO.input(pin)
		setLed(value)

	#Records start time
	startTime = datetime.now()
	print("Starttime: {0} - sensor now should be 0 (start pulse) it is {1}".format(startTime, value))
	while True:
		#If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime #Calculate the time of pulse
			startTime = now #Reset start time
#			print("Startime: {0} - value toggled to {1} - Pulse of value {2} duration {3} detected ".format(startTime, value, previousValue, pulseTime))
			command.append((previousValue, pulseTime.microseconds)) #Store recorded data

		#Updates consecutive 1s variable
		if value:
			num1s += 1
		else:
			num1s = 0

		#Breaks program when the amount of 1s surpasses 10000
		if num1s > 10000:
			now = datetime.now()
			print("Time    : {0} - breaking after {1} consecutive ones - elapsed time {2}.".format(now, num1s, now-startTime))
			break

		#Re-reads pin
		previousValue = value
		value = GPIO.input(pin)
		setLed(value)

	#Converts times to binary
	print("Command array which has {0} elements:".format(len(command)))
	print command
	cnt = 0
	for (typ, tme) in command:
		if typ == 0:
			cnt += 1
	print("Command array has {0} ZERO (mark) elements".format(cnt))
	cnt = 0
	binzero=0
	binone=0
	for (typ, tme) in command:
		if typ == 1:
			cnt += 1
			print("Data bit with tmp = {0}".format(tme))
			if tme > 1000:
				binone += 1
			else:
				binzero +=1
	print("Command array has {0} ONE (space) elements out of which {1} are binary 0 and {2} are binary 1".format(cnt, binzero, binone))

	print("Converting pulses to binary number...")
	for (typ, tme) in command:
		if typ == 1: #If looking at rest period
			if tme > 1600: 
				print("Ignoring leadin space with duration", tme)
			elif tme > 1000: #If pulse greater than 1000us
				binary = binary *10 +1 #Must be 1
			else:
				binary *= 10 #Must be 0
	print("Result = ", binary)
#	if len(str(binary)) > 34: #Sometimes, there is some stray characters
#		binary = int(str(binary)[:34])

	return binary

#Conver value to hex
def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) #Tempary propper base 2
	return hex(tmpB2)

while True:
	inData = convertHex(getBinary()) #Runs subs to get incomming hex value
#        inData = GPIO.input(pin)
	print(inData)
#        time.sleep(0.5)
