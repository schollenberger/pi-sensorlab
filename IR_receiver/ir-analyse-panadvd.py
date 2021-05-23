#-----------------------------------------#
# Name - ir-analyse-panadvd.py
# Description - Code to read data from an IR sensor, analyse it and decode raw message values
#               Version for Panasonic DVD remote
# Author - Werner Schollenberger
# Reference  - Code from Lime Parallelogram
#              https://github.com/Lime-Parallelogram/IR-Code-Referencer
# Licence - Completely Free
# Date - 2021-05-03
#------------------------------------------------------------#

#Import modules
import time
import RPi.GPIO as GPIO
from datetime import datetime

#Static program vars
pin = 11     # GPIO 17 Input - IR sensor out (GPIO.BOARD)
ledpin = 13  # GPIO 27 Output - LED Green (GPIO.BOARD)

# Flag to print out debug message
f_debug = False
## f_debug = True

# Space encoding parameters
t_header_mark = 3000	# This the first mark that determines message begin
t_header_space = 1700   # space that follows after the header mark
num_read_gap = 10000
##num_read_gap = 8000	# number of subsequent spaces to signla EOM - for Panasonic VEG0615

# Note:
#  if t_space_one < t_space_zero : the value has to be less than t_space_one for a logical one
#				   and greater t_space_zero for a logical zero.
#  if t_space_one > t_space_zero : the value has to be greater than t_space_one for a logical one
#                                  and less than t_space_zero for a logical zero.
t_space_one = 1100
t_space_zero = 500

# Whether the last bit should be deleted or not
f_delTrailBit = False

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
	binary = 0 #The bianry value
	command = [] #The list to store pulse times in
	previousValue = 0 #The last value
	value = GPIO.input(pin) #The current value
	setLed(value)
	print('Initial sensor value = {0} - waiting to become 0 (active / mark).'.format(value))
	#Waits for the sensor to pull pin low
	while value:
		value = GPIO.input(pin)
		setLed(value)

	#Records start time
	startTime = datetime.now()
	num1s = 0
	num0s = 0
##	print("Starttime: {0} - sensor changed to 0 (start pulse)".format(startTime))
	while True:
		#If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime #Calculate the time of pulse
			startTime = now #Reset start time
##			print("Startime: {0} - value toggled to {1} - Pulse of value {2} duration {3} detected - {4} / {5}".format(startTime, value, previousValue, pulseTime, num1s, num0s))
			if previousValue:
				num_cnt = num1s
			else:
				num_cnt = num0s
			command.append((previousValue, pulseTime.microseconds, num_cnt)) #Store recorded data

		#Updates consecutive 1s variable
		if value:
			num1s += 1
			num0s = 0
		else:
			num1s = 0
			num0s += 1

		#Breaks program when the amount of 1s surpasses 10000
		if num1s > num_read_gap:
			now = datetime.now()
			if f_debug:
				print("Time     : {0} - breaking after {1} consecutive ones - elapsed time {2}.".format(now, num1s, now-startTime))
			break

		#Re-reads pin
		previousValue = value
		value = GPIO.input(pin)
		setLed(value)

	# Analyze pulse pattern
	if f_debug:
		print("Command array which has {0} elements:".format(len(command)))
		print command

		cnt_mark = 0
		cnt_space = 0
		for (typ, tme, rcnt) in command:
			if typ == 0:
				cnt_mark += 1
			else:
				cnt_space += 1
##	print("Command array has {0} ZERO (mark) elements and {1} SPACE elements".format(cnt_mark, cnt_space))

	if f_debug:
		print
		cnt = 0
		print "Mark durations:  ",
		for (typ, tme, rcnt) in command:
			if typ == 0:
				print "%5d" % tme,
		print
		print "-----"

		print "Space durations: ",
		for (typ, tme, rcnt) in command:
			if typ == 1:
				print "%5d" % tme,
		print
		print "-----"


	print("Converting pulses to binary number...")
	cnt = 0
	res = 0
	bit_read = 0
	for (typ, tme, rcnt) in command:
		if typ == 1: # space, this is the importand piece
			if tme > t_header_space:
				if f_debug:
					print("Ignoring space at position {0} with duration {1}".format(cnt, tme))
				if cnt > 2:
					print("** Message read error - header space at position {} **".format(cnt))
					binary = 0
					res = 0
					break
			elif t_space_one < t_space_zero:
				if tme < t_space_one: # we read a logical 1
					bit_read = 1
				elif tme > t_space_zero:  # we read a logical 0
					bit_read = 0
				else:
					print("Bit read error on bit {0:2d} - tme = {1:5d} - not less than one duration {2} - not greater than zero duration {3}".format(cnt, tme, t_space_one, t_space_zero))
					bit_read = 0
			elif t_space_one > t_space_zero:
				if tme > t_space_one: # we read a logical 1
					bit_read = 1
				elif tme < t_space_zero:  # we read a logical 0
					bit_read = 0
				else:
					print("Bit read error on bit {0:2d} - tme = {1:5d} - not greater than one duration {2} - not less than zero duration {3}".format(cnt, tme, t_space_one, t_space_zero))
					bit_read = 0
			else:
				print("** Internal error in determining logical value from space duration **")
				break
			if f_debug:
				print(" - Bit {0:2d} - {1}".format(cnt, bit_read))
			binary = binary *10 + bit_read
			res = (res<<1) + bit_read
			cnt += 1 # increment bit counter
			if f_debug:
				if cnt %  4 == 0:
					print(" - result = {0:b}".format(res))
		else:  # mark
			if tme > t_header_mark:
				print "Message Header mark detected."
	if f_delTrailBit:
		print "Removing last bit"
		binary = int(binary / 10)
		res = res>>1

	print("Binary result = {0:064d}".format(binary))
	print("Result in hex = {0:016x}".format(res))
	print("Result in bin = {0:064b}".format(res))

#	if len(str(binary)) > 34: #Sometimes, there is some stray characters
#		binary = int(str(binary)[:34])

	return binary

#Conver value to hex
def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) #Tempary propper base 2
	return hex(tmpB2)

try:
	while True:
		inData = convertHex(getBinary()) #Runs subs to get incomming hex value
#	        inData = GPIO.input(pin)
		print(inData)
#	        time.sleep(0.5)
except KeyboardInterrupt:
	pass
	print "*** KeyboardInterrupt caught ***"
	GPIO.output(ledpin, GPIO.LOW)
	GPIO.cleanup()
