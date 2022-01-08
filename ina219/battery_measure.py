#!/usr/bin/python
#
# battery_measure.py
#
# controls battery discharge via relais 
#
from ina219 import INA219, DeviceRangeError
import RPi.GPIO as GPIO
from time import sleep

SHUNT_OHM = 0.1
MAX_STROMSTAERKE = 0.4
RELAY_IO = 17

ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_IO,  GPIO.OUT)

def read_ina219():
    try:
        Ushunt = ina.shunt_voltage()
        Uina = ina.voltage()
        Uges = Uina + Ushunt/1000
        print('Ubat   : {0:0.2f} V'.format(Uges))
        print('Iges   : {0:0.2f} mA'.format(ina.current()))
        print('Pges   : {0:0.2f} mW'.format(ina.power()))
        print('UShunt : {0:0.2f} mV'.format(Ushunt))
        print
    except DeviceRangeError as e:
        print("Stromstaerke zu hoch.")

def turn_on():
    GPIO.output(RELAY_IO, GPIO.HIGH)

def turn_off():
    GPIO.output(RELAY_IO, GPIO.LOW)


try:
#    while 1:
        read_ina219()
        sleep(2)
        read_ina219()
        sleep(2)
        turn_on()
        sleep(1)
        read_ina219()
        sleep(2)
        read_ina219()
        sleep(2)
        read_ina219()
        sleep(2)
        read_ina219()
        sleep(2)
        turn_off()
        sleep(1)

except KeyboardInterrupt:
    pass
    turn_off()
    GPIO.cleanup()
    print
    print("That's all folks ...")
