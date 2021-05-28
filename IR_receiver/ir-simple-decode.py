#!/usr/bin/python2
#-----------------------------------------#
#Name - IR-Finalised.py
#Description - The finalised code to read data from an IR sensor and then refernce it with stored values
#Author - Lime Parallelogram
#Licence - Compleatly Free
#Date - 12/09/2019
#------------------------------------------------------------#
#Imports modules
import RPi.GPIO as GPIO
from datetime import datetime

#Static program vars
pin = 11 #Input pin of sensor (GPIO.BOARD)
# Buttons = [0x300ff9867L,     0x300ffd827L,    0x300ff8877L, 0x300ffa857L, 0x300ffe817L, 0x300ff48b7L, 0x300ff6897L, 0x300ff02fdL, 0x300ff32cdL, 0x300ff20dfL] #HEX code list from original
Buttons =   [0x140040d80820fL, 0x140040d8042cfL, 0x140040d00323fL, 0x140040d001a17L, 0x140040d00a1acL, 0x140040d00616cL, 0x140040d00e1ecL, 0x140040d00111cL, 0x140040d00414cL ] #HEX code list Panasonic DVD RC
ButtonsNames = ["RED",         "GREEN",          "BLUE",           "YELLOW",         "UP",             "DOWN",           "LEFT",           "RIGHT",          "OK"] #String list in same order as HEX list

#Sets up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN)

#IR Protocol constands
num_read_gap = 10000
t_header_space = 1700
t_space_one = 1100
t_space_zero = 500


#Gets binary value
def getBinary():
	#Internal vars
	num1s = 0 #Number of consecutive 1s read
	binary = 1 #The bianry value
	command = [] #The list to store pulse times in
	previousValue = 0 #The last value
	value = GPIO.input(pin) #The current value

	#Waits for the sensor to pull pin low
	while value:
		value = GPIO.input(pin)

	#Records start time
	startTime = datetime.now()

	while True:
		#If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime #Calculate the time of pulse
			startTime = now #Reset start time
			command.append((previousValue, pulseTime.microseconds)) #Store recorded data

		#Updates consecutive 1s variable
		if value:
			num1s += 1
		else:
			num1s = 0

		#Breaks program when the amount of 1s surpasses 10000
		if num1s > num_read_gap:
			break

		#Re-reads pin
		previousValue = value
		value = GPIO.input(pin)

	#Converts times to binary
	header = 0
	for (typ, tme) in command:
		if typ == 1: #If looking at rest period
			if tme > t_header_space:
				header=1  # ignoring header space
			elif tme > t_space_one: #If pulse greater than lowest value - assuming zero duration is shorter
				binary = binary *10 +1 #Must be 1
			else:
				binary *= 10 #Must be 0

	#if len(str(binary)) > 34: #Sometimes, there is some stray characters  ## Panasonic rc uses more bits
	#	binary = int(str(binary)[:34])
#	print("Read binary: {0}".format(binary))
	return binary

#Conver value to hex
def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) #Tempary propper base 2
	return hex(tmpB2)

while True:
	inData = convertHex(getBinary()) #Runs subs to get incomming hex value
#	print("Received message - in hex: {0}".format(inData))
	for button in range(len(Buttons)):#Runs through every value in list
		if hex(Buttons[button]) == inData: #Checks this against incomming
			print(ButtonsNames[button]) #Prints corresponding english name for button

