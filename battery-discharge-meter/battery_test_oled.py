#!/usr/bin/python3

# This program tests the capacity status of a battery,
# rechargable or not by measuring the voltage with and without
# some load.
# To be used with an INA219 Ampere/Voltage meter and a Relais
# to connect the discharge resistor and an OLED display (128x64 pixel)
# to show actual voltage, current and discharge values.
#
# Starting and stopping the discharge test is done via an
# electrical relay connected to GPIO port 17 (board.D17).
#
# It uses the Adafruit Circuit LCD libraries to control the
# ina219 device, relais, and the OLED/LCD display.
#
# It uses an MCP3008 AD converter to measure battery voltage in
# the function ina_read() as the values form the INA219 board
# are not accurate.
#
# This tool supports command line parameters and options.
# The tool uses python logging as well.
#
# Created:  10.03.2022 Werner Schollenberger

import sys
import csv
import os.path
import locale
from datetime import datetime
from time import sleep

from argparse import ArgumentParser
import logging
from logging.config import dictConfig

import board
import digitalio
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
#import adafruit_character_lcd.character_lcd as character_lcd

# Log settings
loglevel_message = 5

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-14s %(levelname)-8s %(message)s'},
        'm': {'format':
              '%(asctime)-12s  ***  %(message)s'},
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG},
        'm': {'class': 'logging.StreamHandler',
              'stream': sys.stdout,
              'formatter': 'm',
              'level': loglevel_message},
        },
    loggers = {
        'message': {'handlers': ['m'],
                    'level': loglevel_message},
        },
    root = {
        'handlers': ['h'],
        'level': logging.WARNING,
        },
)


#sys.path.append('../LCD-Module')
sys.path.append('../oled-display')
sys.path.append('../ad-converter')

from MCP3008 import MCP3008  # AD converter support using SPI bus
adc = MCP3008()
adc_channel = 0
adc_uref = 3.331
adc_range = 4096.0

#import lcd_circuit_ports as plcd
#lcd_columns = 20
#lcd_rows = 4

# OLED support
from PIL import ImageFont
# Luma driver
##from luma.core.interface.serial import i2c
##from luma.oled.device import sh1106, ssd1306
##from oled_luma import OledLuma
# Adafruit driver
from board import SCL, SDA
import busio
import adafruit_ssd1306
from oled_adafruit import OledAdafruit

# We use the log_message() function print "message" to which a different
# logging format applies. We use a special logger named "message" for
# which we have a separate configuration on the logging dictionary.
def log_message(txt):
    logger = logging.getLogger("message")
    logger.log(loglevel_message,txt)


# Helper function to prevent accidential file overwrite
def check_would_overwrite(fn, overwrite):
    result = False
    if os.path.isfile(fn):
        if not overwrite:
            print("ERROR: Must not overwrite existing file {0}  Aborting...".format(fn),
                 file=sys.stderr)
            print("*****  Invoke with overwrite option to avoid this.",
                 file=sys.stderr)

            result = True
            sys.exit()
        else:
            result = True

    return result

# Method to convert a time interval integer into a duration string. Usually
# in the format of "[hh:]mm:ss" but for short values it generates "xx sec".

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


def ina219_init(ina219):
    # optional : change configuration to use 32 samples averaging for both bus voltage
    # and shunt voltage
    ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    # optional : change voltage range to 16V
    ina219.bus_voltage_range = BusVoltageRange.RANGE_16V


def ina219_read(ina219):
    logger = logging.getLogger("ina219_read()")
    Uges = Iina = 0.0
    try:
        Ushunt = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
        Uina = ina219.bus_voltage      # voltage on V- (load side)
#        Uges = Uina
#        Uges = Uina + Ushunt
        Uges = adc.read(adc_channel) * adc_uref / adc_range
        Iina = ina219.current  # current in mA
        Pina = ina219.power # power in watts

        logger.debug('Uges/Uina/Ushunt/Iina/Pina: {0:0.4f} V /  {6:0.4f} V /  {5:0.4f} V / {1:0.2f} mA / {2:0.5f} W - Pbatt {3:0.2f} mW - Pload {4:0.2f} mW'.format(
             Uges,Iina,Pina,Iina*Uges,Iina*Uina,Ushunt,Uina))
#        log_message_display('* BDM * {0:0.2f}V\n{1:0.1f}mA {2:0.1f}mW'.format(Uges,Iina,Iina*Uges))
    except DeviceRangeError as e:
        logger.error("ina219_read(): Range error - current too high.")
        raise

    return Uges,Iina,Iina*Uges

def turn_on(relay_io):
    logger = logging.getLogger("turn_on()")
    logger.debug("Turn relay on")
    relay_io.value = True
    sleep(0.5)

def turn_off(relay_io):
    logger = logging.getLogger("turn_off()")
    logger.debug("Turn relay off")
    relay_io.value = False

def reset_gpio(relay_io):
    logger = logging.getLogger("reset_gpio()")
    logger.debug("Turn relay off")
    turn_off(relay_io)
#    GPIO.cleanup()

def print_display(lcd, txt):
    logger = logging.getLogger("print_display()")
    logger.debug("Printing to OLED display: \n%s", txt)
    lcd.display_text(txt)


def print_start(lcd, uact):
    logger = logging.getLogger("print_start")
    log_message("Battery Tester - starting new measurement...")
    log_message('Initial voltsage: {0:0.2f} V'.format(uact))
    print_display(lcd, '* Battery Tester *\nInit    : {0:0.2f} V\n\nAbout to discharge...'.format(
         uact))


def print_status(lcd, tim, u_init, u_act, i_act):
    logger = logging.getLogger("print_status")
    logger.info(' Status: {0:6d} sec:  Init: {1:5.3f} V  Load: {2:5.3f} V  Current {3:7.2f} mA'.format(tim, u_init, u_act, i_act))

    print_display(lcd, 'Running for {0}\nInit:  {1:5.3f} V \nLoad:  {2:5.3f}V\nCurrent: {3:4.0f}mA'.format(
         duration_to_hhmmss(tim), u_init, u_act, i_act))

def print_final(lcd, tim, u_init, voltage, current, u_end):
    logger = logging.getLogger("print_final")
    log_message('\n** Discharge duration: {0}\n** Initial Voltage:    {1:0.2f} V\n** Load Voltage:       {2:0.2f} V\n** Load Current:             {3:0.2f} mA\n** End Voltage:        {4:0.2f} V'.format(
         duration_to_hhmmss(tim), u_init, voltage, current, u_end))
#    print_display(lcd, 'Done after {0}\nIinit    : {1:0.2f} V\nLoad  :    {2:0.2f} V\nCurrent:  {3:0.3f} mA\nEnd   :    {4:0.2f} V'.format(
    print_display(lcd, 'Iinit    : {1:0.2f} V\nLoad  :    {2:0.2f} V\nCurrent:  {3:0.3f} mA\nEnd   :    {4:0.2f} V'.format(
         duration_to_hhmmss(tim), u_init, voltage, current, u_end))


# Main routine

if __name__ == "__main__":

    logfile_prefix= "battery_test"
    DISCHARGE_INTERVAL = 5  #in seconds - total discharge test time
    wait_init = 3 # in seconds - wait before discharging

    # Argument parsing
    parser = ArgumentParser(
             description='Battery Tester - Shows batter voltage w/ and w/o load.'
             )
    parser.add_argument('-v', '--verbose', action='count', default=0,
                       help='Increase log level -vv is debug.')

    parser.add_argument('-l', '--log_output', action='store_true',
                       help='Logs output to file battery_test.log.')

    parser.add_argument('-o', '--outfile',
                       help='Sets log file name. Overwrites -l option.')

    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite already existing files silently.')

    parser.add_argument('--nowait', action='store_true',
                       help="Don't wait before discharging.")

    parser.add_argument('-q', '--quicktest', action='store_true',
                       help="Quick test, no wait before discharging and only one load test.")


    args = parser.parse_args()

    # Prepare logging
    files_overwrite = args.overwrite
    logfile = None
    logfile_name = None

    logging.config.dictConfig(logging_config)
    # prepare for message logging on file
    logging.addLevelName(loglevel_message, 'OUTPUT')

    if args.verbose > 0:
        if args.verbose == 1:
            logging.root.setLevel(logging.INFO)
        else:
            logging.root.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    logger.debug("Verbose counter = %s", args.verbose)
    logger.info("Log level = %s.",
         logging.getLevelName(logging.root.getEffectiveLevel())
         )

    if args.log_output:
        # Create log file name from prefix and optionally timestamp
        logfile_name = logfile_prefix+ ".log"
        logger.debug("Set logfile_name to %s", logfile_name)

    if args.outfile:
        logfile_name = args.outfile
        logger.debug("Got logfile_name from command line: %s", logfile_name)

    if logfile_name:
        if check_would_overwrite(logfile_name, files_overwrite):
           # Note what function above aborts for existing file and overwrite = False
            logger.warn("Overwriting existing log file <{0}>".format(logfile_name))

        logfile = open(logfile_name, 'w')

        _fmt = logging.Formatter(logging_config['formatters']['f']['format'])
        _handler = logging.StreamHandler(logfile)
#        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(_fmt)
        logging.root.addHandler(_handler)
        logger.info("Logging to file %s - set console logging to WARNING.",
                     logfile_name)
        ch = logging.root.handlers[0]
        ch.setLevel(logging.WARNING)

    if args.nowait:
        wait_init = 0

    if args.quicktest:
        wait_init = 0
        DISCHARGE_INTERVAL = 0

    # Initialize peripheral hardware components

    # INA board
    i2c_bus = board.I2C()
    ina     = INA219(i2c_bus)
    ina219_init(ina)

    # electrical relay
    relay_io = digitalio.DigitalInOut(board.D17)
    relay_io.direction = digitalio.Direction.OUTPUT

    # OLED display
    oled_font = ImageFont.truetype('DejaVuSansMono.ttf', 10)

    # Luma compatible i2c and device objects
    ##luma_i2c = i2c(port=1, address=0x3C)
    ##luma_dev = ssd1306(luma_i2c)
    ## #luma_dev = sh1106(luma_i2c)
    ## lcd = OledLuma(luma_dev, oled_font)

    # Adafruit compatible i2c and device objects
    ada_i2c = busio.I2C(SCL, SDA)
    ada_dev = adafruit_ssd1306.SSD1306_I2C(128, 64, ada_i2c)
    lcd = OledAdafruit(ada_dev, oled_font)

#    lcd.greeting("Battery Tester")
#    sleep(5)

    # LCD display
#    lcd = character_lcd.Character_LCD_Mono(plcd.rs, plcd.en, plcd.d4, plcd.d5, plcd.d6, plcd.d7,
#               lcd_columns, lcd_rows, plcd.backlight, True)
#    lcd.clear()


    # Read initial battery voltage then start discharging for some time and then
    # meansure voltage and current
    try:
        Uactual,Iactual,Pactual = ina219_read(ina)
        Uinit = Uactual
        print_start(lcd, Uinit)
        sleep(wait_init)
        log_message("Start discharging at {:0.3f} V...".format(Uinit))
        turn_on(relay_io)
        time_discharge = 0

        while time_discharge <= DISCHARGE_INTERVAL:
            sleep(1)
            Uactual,Iactual,Pactual = ina219_read(ina)
            print_status(lcd, time_discharge, Uinit, Uactual, Iactual)
            time_discharge  += 1

        log_message('Stopping discharge...')
        turn_off(relay_io)
        Uload = Uactual
        if not args.quicktest:
            print_display(lcd, "Stopped at {0:0.3} V\n\nLet battery recover...".format(Uload))
            sleep(1)
            time_discharge  += 1
            Uactual,dummy,dummy = ina219_read(ina)
            log_message('Voltage after discharge end: {0:0.3f} V'.format(Uactual))

            log_message('Waiting another few seconds to let the battery relax')
            sleep(1)
            time_discharge  += 1
            Uactual,dummy,dummy = ina219_read(ina)
            log_message('Voltage discharged battery:  {0:0.3f} V'.format(Uactual))

        print_final(lcd, time_discharge, Uinit, Uload, Iactual, Uactual)
#        logger.info("Waiting 5 sec so before closing, so you can read the display")
#        sleep(5)

    except KeyboardInterrupt:
        log_message("Keyboard interrupt - while discharging! Last voltage: {0:0.3f} V".format(Uactual))
        print_display(lcd, "Interrupted....\n{0}  {1:0.2f} mA\nVoltage:  {2:0.3f} V".format(duration_to_hhmmss(time_discharge),
             Iactual, Uactual))
#        sleep_time = 5
#        logger.info("Waiting {0:d} sec so before closing, so you can read the display".format(sleep_time))
#        sleep(sleep_time)

    finally:
    #    pass
        reset_gpio(relay_io)
        if hasattr(logfile, "close"):
            logger.info("Closing log file...")
            logfile.close()

