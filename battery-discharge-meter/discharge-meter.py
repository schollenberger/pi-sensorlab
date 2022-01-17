#!/usr/bin/python

from ina219 import INA219, DeviceRangeError
import RPi.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep

import sys

# discharge low voltage = 1.0 V (NiMH) / 0.85 - 1 V (NiCd)
# see: https://de.wikipedia.org/wiki/Tiefentladung
#       https://de.wikipedia.org/wiki/Entladeschlussspannung

SHUNT_OHM = 0.1
MAX_STROMSTAERKE = 0.4
UMIN = 1.00  # Volts discharge low voltage
#UMIN = 1.10  # Volts discharge low voltage for test purposes
DISCHARGE_INTERVAL = 5  #seconds

ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

RELAY_IO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_IO,  GPIO.OUT)

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
                       cols=16, lines=2)
lcd.clear()

# we use the log_message() function to allow program to run in background and retrieve latest messages from stdout (nohup.out)

def log_message(txt):
    print(txt)
    sys.stdout.flush()


def print_display(txt):
    lcd.clear()
    lcd.message(txt)

def format_duration(duration):
    durtxt = 'undefined'
    if duration < 60:
         durtxt = '  {0:2d} sec'.format(duration)
    elif duration < 3600:
         hr,sec = divmod(duration,60)
         durtxt = '   {0:2d}:{1:2d}'.format(hr,sec)

    return durtxt

def read_ina219():
    Uges = Iina = 0.0
    try:
        Ushunt = ina.shunt_voltage()
        Uina = ina.voltage()
#        Uges = Uina
        Uges = Uina + Ushunt/1000
        Iina = ina.current()
        Pina = ina.power()
        log_message('Ubat/I/P: {0:0.4f} V  / {1:0.4f} mA / {2:0.4f} mW - calculated P {3:0.4f} mW'.format(Uges,Iina,Pina,Iina*Uges))
#        print_display('* BDM * {0:0.2f}V\n{1:0.1f}mA {2:0.1f}mW'.format(Uges,Iina,Iina*Uges))
        # print('Pges   : {0:0.2f} mW'.format(Pina))
        # print('UShunt : {0:0.2f} mV'.format(Ushunt))
        print
    except DeviceRangeError as e:
        log_message("Stromstaerke zu hoch.")

    return Uges,Iina,Iina*Uges

def turn_on():
    GPIO.output(RELAY_IO, GPIO.HIGH)
    sleep(0.5)

def turn_off():
    GPIO.output(RELAY_IO, GPIO.LOW)

def reset_gpio():
    turn_off()
    GPIO.cleanup()

def print_status(tim, discharge, power):
    log_message('-- {0} sec: Entladung: {1:0.6f} mAh  Energie: {2:0.6f} mWh'.format(tim, discharge, power))

def print_final(tim, discharge, power):
    lop_message('Dauer: {0} min - Entladung: {1:0.4} mAh  Energie: {2:0.4f} mWh'.format(tim/60, discharge, power))
    print_display('Done after {0} min\n{1:0.2f} mAh {2:0.2f}mWh'.format(tim/60, discharge, power))

try:
    TotalDischarge = 0.0
    TotalPower = 0.0
    TimeDischarge = 0 # in seconds

    Uactual,dummy,dummy = read_ina219()
    if Uactual <= UMIN:
        log_message('Batterie / Akku hat eine zu geringe Spannung: {0:0.2f} V'.format(Uactual))
    else:
        log_message('Initiale Spannung: {0:0.2f} V'.format(Uactual))
        log_message("Beginne mit der Entladung...")
        turn_on()
        print_status(0, TotalDischarge, TotalPower)
        while Uactual > UMIN:
            Uactual,Iactual,Pactual = read_ina219()
            print_display('{0:8d}s   {1:6.2f}V\n{3:8.1f}mAh {2:6.2f}mA'.format(TimeDischarge,Uactual,Iactual,TotalDischarge))
            sleep(DISCHARGE_INTERVAL)
            TimeDischarge  += DISCHARGE_INTERVAL
            TotalDischarge += Iactual * DISCHARGE_INTERVAL/3600
            TotalPower     += Pactual *  DISCHARGE_INTERVAL/3600
            print_status(TimeDischarge, TotalDischarge, TotalPower)
        log_message('Entladeschlussspannung unterschritten -  Batterie/Akku-Spannung: {0:0.2f} V'.format(Uactual))
        log_message('Beende Entladung...')
        turn_off()
        sleep(1)
        Uactual,dummy,dummy = read_ina219()
        log_message('Spannung nach Ladeschluss: {0:0.2f} V'.format(Uactual))
        print_final(TimeDischarge, TotalDischarge, TotalPower)

except KeyboardInterrupt:
    print
    log_message("Keyboard interrupt - while discharging  ...")
    print_display("Interrupted....\n{0} s {1:0.2f} mAh".format(TimeDischarge,TotalDischarge))

finally:
#    pass
#    sleep(0.5)
    reset_gpio()
#    print('Dauer: {0} min - Entladung: {1:0.6f} mAh  Energie: {2:0.6f} mWh'.format(TimeDischarge/60, TotalDischarge, TotalPower))
