#!/usr/bin/python3

# Records discharge characteristics of batteries
# To be used with an INA219 Ampere/Voltage meter and a Relais
# to connect the discharge resistor and a LCD display (4x20 chars)
# to show actual voltage, current and discharge values.
#
# It stops discharging when the battery voltage drops below a
# minimum discharge value.
#
# It writes the discharge voltage characteristics into a CSV file.
# It uses the Adafruit Circuit LCD libraries to control the
# ina219 device, relais, and the LCD display.
#
# Created:  18.01.2022 Werner Schollenberger

import board
import digitalio
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import adafruit_character_lcd.character_lcd as character_lcd

from time import sleep

import sys
import csv
import os.path
import locale
from datetime import datetime
sys.path.append('../LCD-Module')

import lcd_circuit_ports as plcd
lcd_columns = 20
lcd_rows = 4

# discharge low voltage = 1.0 V (NiMH) / 0.85 - 1 V (NiCd)
# see: https://de.wikipedia.org/wiki/Tiefentladung
#       https://de.wikipedia.org/wiki/Entladeschlussspannung

UMIN = 1.00  # Volts discharge low voltage
#UMIN = 1.10  # Volts discharge low voltage for test purposes
DISCHARGE_INTERVAL = 5  #seconds


# we use the log_message() function to allow program to run in background
# and retrieve latest messages from stdout (nohup.out)

# CSV class to log discharge statistics
class DischargeCsv:

    def __init__(self, filename="",overwrite = False):
        try:
            locale_name = 'de_DE.utf8'
#            locale_name = 'de_DE'
            locale.setlocale(locale.LC_ALL,locale_name)
        except locale.Error as e:
            print("WARN: Could not set locale for CSV file to <{0}> - ignoring.".format(
                 locale_name))
            print("WARN: locale.setlocale() Error message: <{0}>".format(e))

        if len(filename) == 0:
             today = datetime.now()
             self.fn = "discharge-{0:4d}-{1:02d}-{2:02d}_{3:02d}{4:02d}.csv".format(
                            today.year,today.month,today.day,today.hour,today.minute)

        if os.path.isfile(self.fn):
       	    if not overwrite:
                print("ERROR: CSV file {0} already exists - Aborting!.".format(self.fn))
                sys.exit()
            else:
                print("WARN: Overwriting existing CSV file <{0}>".format(self.fn))
        else:
             print("Writing to CSV file: {0}".format(self.fn))

        self.csv_file = open(self.fn, 'w')

        self.csv_writer = csv.writer(self.csv_file, delimiter=";")
        self.csv_writer.writerow(["Time/sec","Ubat/V","Umin+/V", "Icurrent/mA",
             "Pcurrent/mW","TotalDischarge/mAh","TotalPower/mWh"])

    def write(self, tim, u_act, i_act, p_act, t_discharge, t_power):
        if self.csv_writer:
            self.csv_writer.writerow([locale.format_string('%d',tim),
                                      locale.format_string('%0.4f',u_act),
                                      locale.format_string('%0.4f',u_act-UMIN),
                                      locale.format_string('%0.2f',i_act),
                                      locale.format_string('%0.2f',p_act),
                                      locale.format_string('%0.2f',t_discharge),
                                      locale.format_string('%0.2f',t_power)])

        #print(' *CSV* {0};{1:0.2f};{2:0.2f};{3:0.2f};{4:0.4f};{5:0.4f}'.format(
        #     tim,u_act,u_act-UMIN,i_act,p_act,t_discharge,t_power))

    def close(self):
        if self.csv_file:
            print("Closing CSV file...")
            self.csv_file.close()
        else:
            print("DischarchCsv.close(): Nothing to close!!")


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
              durtxt = '   {0:02d}:{1:02d}'.format(mm,ss)
         else:
              hh,mm = divmod(mm,60)
              durtxt ='{0:02d}:{1:02d}:{2:02d}'.format(hh,mm,ss)

    return durtxt

def print_display(lcd, txt):
    lcd.clear()
    lcd.message = txt

def ina219_init(ina219):
    # optional : change configuration to use 32 samples averaging for both bus voltage
    # and shunt voltage
    ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    # optional : change voltage range to 16V
    ina219.bus_voltage_range = BusVoltageRange.RANGE_16V


def ina219_read(ina219):
    Uges = Iina = 0.0
    try:
        pass
        Ushunt = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
        Uina = ina219.bus_voltage      # voltage on V- (load side)
#        Uges = Uina
        Uges = Uina + Ushunt
        Iina = ina219.current  # current in mA
        Pina = ina219.power # power in watts

##        log_message('Ubat/Ushunt/I/P: {0:0.5f} V /  {5:0.5f} V / {1:0.4f} mA / {2:0.4f} W - Pbatt {3:0.4f} mW - Pload {4:0.4f} mW'.format(
##             Uges,Iina,Pina,Iina*Uges,Iina*Uina,Ushunt))
#        print_display('* BDM * {0:0.2f}V\n{1:0.1f}mA {2:0.1f}mW'.format(Uges,Iina,Iina*Uges))
        # print('Pges   : {0:0.2f} mW'.format(Pina))
        # print('UShunt : {0:0.2f} mV'.format(Ushunt))
    except DeviceRangeError as e:
        log_message("ina219_read(): Range error - current too high.")
        raise

    return Uges,Iina,Iina*Uges

def turn_on(relay_io):
    relay_io.value = True
    sleep(0.5)

def turn_off(relay_io):
    relay_io.value = False

def reset_gpio(relay_io):
    turn_off(relay_io)
#    GPIO.cleanup()

def print_start(lcd, uact,battery_low=False):
    if battery_low:
         log_message('Battery voltage of {0:0.2f} V is too low for discharging it has to be at least {1:0.2f} V'.format(
              Uactual, UMIN))
         print_display(lcd, '* Discharge meter *\nBattery low: {0:0.2f} V\nAborting...'.format(
              uact))
    else:
         log_message('Initial voltage: {0:0.2f} V'.format(uact))
         print_display(lcd, '* Discharge meter *\nIdle at   {0:0.3f} V\n\nStarting discharge.'.format(
              uact))


def print_status(lcd, tim, u_act, i_act, p_act, t_discharge, t_power):
    log_message(' -- {0:6d} sec:  {1:5.4f} V  {2:7.2f} mA  {3:7.2f} mW  {4:8.2f} mAh  {5:8.2f}mWh'.format(
         tim,u_act,i_act,p_act,t_discharge,t_power))
#    print_display(lcd, 'Run     {0}\n{1:0.2f}V {2:0.0f}mA {3:0.0f}mAh '.format(duration_to_hhmmss(tim),
#         u_act,i_act,t_discharge))
    print_display(lcd, 'Running for {0}\n   {1:5.3f}V    {2:4.0f}mA\n   {3:5.0f}mAh {3:5.0f}mWh'.format(
         duration_to_hhmmss(tim),u_act,i_act,t_discharge, t_power))

def print_final(lcd, tim, discharge, power, voltage):
    log_message('** Discharge duration: {0}\n** Total discharge:    {1:0.2f} mAh\n** Total energy:       {2:0.2f} mWh\n** Voltage:            {3:0.3f}V '.format(
         duration_to_hhmmss(tim), discharge, power, voltage))
    print_display(lcd, 'Done after {0}\nCapacity: {1:0.2f}mAh\nPower:    {2:0.2f}mWh\nVoltage:  {3:0.3f}V'.format(
         duration_to_hhmmss(tim), discharge, power, voltage))

if __name__ == "__main__":
    i2c_bus = board.I2C()
    ina     = INA219(i2c_bus)
    ina219_init(ina)

    relay_io = digitalio.DigitalInOut(board.D17)
    relay_io.direction = digitalio.Direction.OUTPUT

    lcd = character_lcd.Character_LCD_Mono(plcd.rs, plcd.en, plcd.d4, plcd.d5, plcd.d6, plcd.d7,
               lcd_columns, lcd_rows, plcd.backlight, True)
    lcd.clear()

    try:
        TotalDischarge = 0.0
        TotalPower = 0.0
        TimeDischarge = 0 # in seconds
        csv_last_uactual = csv_last_time = 0.0

        Uactual,Iactual,Pactual = ina219_read(ina)
        if Uactual <= UMIN:
            print_start(lcd, Uactual, battery_low=True)
        else:
            print_start(lcd, Uactual, battery_low=False)

            csvfile = DischargeCsv()
#            csvfile = DischargeCsv("discharge.csv", overwrite=True)
            csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)

            sleep(5)
            log_message("Start discharging...")
            turn_on(relay_io)
            sleep(1)
            TimeDischarge  += 1
            Uactual,Iactual,Pactual = ina219_read(ina)
            print_status(lcd, TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge, TotalPower)
            csvfile.write(TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge, TotalPower)
            csv_last_uactual = Uactual
            csv_last_time =  TimeDischarge
            csv_delta_u = (Uactual - UMIN)/20.0
            log_message("Voltage difference to trigger new CSV entry: {0:0.4f}".format(csv_delta_u))

            while Uactual > UMIN:
                if TimeDischarge < DISCHARGE_INTERVAL:
                    delay = DISCHARGE_INTERVAL-TimeDischarge
                    sleep(delay)
                    TimeDischarge  += delay
                else:
                    sleep(DISCHARGE_INTERVAL)
                    TimeDischarge  += DISCHARGE_INTERVAL
                TotalDischarge += Iactual * DISCHARGE_INTERVAL/3600
                TotalPower     += Pactual *  DISCHARGE_INTERVAL/3600
                print_status(lcd, TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge,
                     TotalPower)
                # reduce number of rows in CSV file
                if (abs(csv_last_uactual - Uactual) > csv_delta_u) or ((TimeDischarge - csv_last_time )> 60):
                     log_message("-- new row in CSV file --")
                     csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)
                     csv_last_uactual = Uactual
                     csv_last_time =  TimeDischarge

                # read new value
                Uactual,Iactual,Pactual = ina219_read(ina)

            log_message('Current battery voltage of {0:0.2f} V dropped below mimimum of {1:0.2f} V'.format(
                 Uactual, UMIN))
            log_message('-- new row in CSV file ..')
            csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)

            log_message('Stopping discharge...')
            turn_off(relay_io)
            sleep(1)
            Uactual,dummy,dummy = ina219_read(ina)
            log_message('Voltage after discharge end: {0:0.3f} V'.format(Uactual))
            csvfile.write(TimeDischarge+1, Uactual, 0.0, 0.0, TotalDischarge, TotalPower)
            log_message('Waiting another few seconds to let the battery relax')
            sleep(5)
            Uactual,dummy,dummy = ina219_read(ina)
            log_message('Voltage discharged battery:  {0:0.3f} V'.format(Uactual))
            csvfile.write(TimeDischarge+1, Uactual, 0.0, 0.0, TotalDischarge, TotalPower)

            csvfile.close()
            print_final(lcd, TimeDischarge, TotalDischarge, TotalPower, Uactual)

    except KeyboardInterrupt:
        log_message("Keyboard interrupt - while discharging  ... Last voltage: {0:0.3f}V".format(Uactual))
        print_display(lcd, "Interrupted....\n{0}  {1:0.2f} mAh\nVoltage:  {2:0.3f}V".format(duration_to_hhmmss(TimeDischarge),
             TotalDischarge, Uactual))

    finally:
    #    pass
        reset_gpio(relay_io)
