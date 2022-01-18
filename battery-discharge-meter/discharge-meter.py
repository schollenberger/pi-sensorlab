#!/usr/bin/python

# Records discharge characteristics of batteries
# To be used with an INA219 Ampere/Voltage meter and a Relais 
# to connect the discharge resistor and a LCD display to show
# actual voltage, current and discharge values.
#
# It stops discharging when the battery voltage drops below a
# minimum discharge value.
#
# 18.01.2022 Werner Schollenberger

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

class DischargeCsv:
# CSV class to log discharge statistics

    fn = ""

    def __init__(self, filename="discharge.out"):
        fn = filename

    def write(self, tim, u_act, i_act, p_act, t_discharge, t_power):
        pass
        #print(' *CSV* {0};{1:0.2f};{2:0.2f};{3:0.2f};{4:0.4f};{5:0.4f}'.format(tim,u_act,i_act,p_act,t_discharge,t_power))

    def close(self):
         pass


def log_message(txt):
    print(txt)
    sys.stdout.flush()

def duration_to_hhmmss(duration):
    durtxt = 'undefined'
    if duration < 60:
         durtxt = '  {0:2d} sec'.format(duration)
    else:
         mm,ss = divmod(duration,60)
         if duration < 3600:
              durtxt = '   {0:2d}:{1:2d}'.format(mm,ss)
         else:
              hh,mm = divmod(mm,60)
              durtxt ='{0:02d}:{1:02d}:{2:02d}'.format(hh,mm,ss)

    return durtxt

def print_display(txt):
    lcd.clear()
    lcd.message(txt)

def read_ina219():
    Uges = Iina = 0.0
    try:
        Ushunt = ina.shunt_voltage()
        Uina = ina.voltage()
#        Uges = Uina
        Uges = Uina + Ushunt/1000
        Iina = ina.current()
        Pina = ina.power()
        # log_message('Ubat/I/P: {0:0.4f} V  / {1:0.4f} mA / {2:0.4f} mW - calculated P {3:0.4f} mW'.format(Uges,Iina,Pina,Iina*Uges))
#        print_display('* BDM * {0:0.2f}V\n{1:0.1f}mA {2:0.1f}mW'.format(Uges,Iina,Iina*Uges))
        # print('Pges   : {0:0.2f} mW'.format(Pina))
        # print('UShunt : {0:0.2f} mV'.format(Ushunt))
    except DeviceRangeError as e:
        log_message("read_ina219(): Range error - current too high.")
        raise

    return Uges,Iina,Iina*Uges

def turn_on():
    GPIO.output(RELAY_IO, GPIO.HIGH)
    sleep(0.5)

def turn_off():
    GPIO.output(RELAY_IO, GPIO.LOW)

def reset_gpio():
    turn_off()
    GPIO.cleanup()

def print_status(tim, u_act, i_act, p_act, t_discharge, t_power):
    log_message(' -- {0:6d} sec:  {1:5.2f} V  {2:7.2f} mA  {3:7.2f} mW  {4:8.2f} mAh  {5:8.2f}mWh'.format(tim,u_act,i_act,p_act,t_discharge,t_power))
    print_display('Run     {0}\n{1:0.2f}V {2:0.0f}mA {3:0.0f}mAh '.format(duration_to_hhmmss(tim),u_act,i_act,t_discharge))

def print_final(tim, discharge, power):
    log_message('** Discharge duration: {0}\n** Total discharge:    {1:0.2f} mAh\n** Total energy:       {2:0.2f} mWh'.format(duration_to_hhmmss(tim), discharge, power))
    print_display('Done   {0}\n{1:0.2f} mAh {2:0.2f}mWh'.format(duration_to_hhmmss(tim), discharge, power))

try:
    TotalDischarge = 0.0
    TotalPower = 0.0
    TimeDischarge = 0 # in seconds

    csvfile = DischargeCsv()

    Uactual,Iactual,Pactual = read_ina219()
    if Uactual <= UMIN:
        log_message('Battery voltage of {0:0.2f} V is too low for discharging it has to be at least {1:0.2f} V'.format(Uactual, UMIN))
        print_display('Battery low: {0:0.2f} V\n'.format(Uactual))
    else:
        log_message('Initial voltage: {0:0.2f} V'.format(Uactual))
        print_display('Idle    {0:0.2f} V'.format(Uactual))
        sleep(5)
        csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)
        log_message("Start discharging...")
        turn_on()
        sleep(1)
        TimeDischarge  += 1
        Uactual,Iactual,Pactual = read_ina219()
        print_status(TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge, TotalPower)
        csvfile.write(TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge, TotalPower)
        while Uactual > UMIN:
            Uactual,Iactual,Pactual = read_ina219()
            if TimeDischarge < DISCHARGE_INTERVAL:
                delay = DISCHARGE_INTERVAL-TimeDischarge
                sleep(delay)
                TimeDischarge  += delay
            else:
                sleep(DISCHARGE_INTERVAL)
                TimeDischarge  += DISCHARGE_INTERVAL
            TotalDischarge += Iactual * DISCHARGE_INTERVAL/3600
            TotalPower     += Pactual *  DISCHARGE_INTERVAL/3600
            print_status(TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge, TotalPower)
            csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)

        log_message('Current battery voltage of {0:0.2f} V dropped below mimimum of {1:0.2f} V'.format(Uactual, UMIN))
        log_message('Stopping discharge...')
        turn_off()
        sleep(1)
        Uactual,dummy,dummy = read_ina219()
        log_message('Spannung nach Ladeschluss: {0:0.2f} V'.format(Uactual))
        csvfile.write(TimeDischarge+1, Uactual, 0.0, 0.0, TotalDischarge, TotalPower)
        csvfile.close()
        print_final(TimeDischarge, TotalDischarge, TotalPower)

except KeyboardInterrupt:
    log_message("Keyboard interrupt - while discharging  ...")
    print_display("Interrupted....\n{0}  {1:0.2f} mAh".format(duration_to_hhmmss(TimeDischarge),TotalDischarge))

finally:
#    pass
    reset_gpio()
