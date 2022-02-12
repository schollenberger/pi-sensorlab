#!/usr/bin/python3

# This program records discharge characteristics of batteries
# To be used with an INA219 Ampere/Voltage meter and a Relais
# to connect the discharge resistor and an OLED display (128x64 pixel)
# to show actual voltage, current and discharge values.
#
# It stops discharging when the battery voltage drops below a
# minimum discharge value.
# Starting and stopping the discharge process is done via an
# electrical relay connected to GPIO port 17 (board.D17).
#
# It writes the discharge voltage characteristics into a CSV file.
# It uses the Adafruit Circuit LCD libraries to control the
# ina219 device, relais, and the LCD display.
#
# It uses an MCP3008 AD converter to measure battery voltage in
# the function ina_read() as the values form the INA219 board
# are not accurate.
#
# This tool supports command line parameters and options.
# The tool uses python logging as well.
#
# Created:  12.02.2022 Werner Schollenberger

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
import adafruit_character_lcd.character_lcd as character_lcd

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

# OLED SH1106 support
from luma.core.interface.serial import i2c
from PIL import ImageFont
from oled_sh1106 import OledSh1106


# discharge low voltage = 1.0 V (NiMH) / 0.85 - 1 V (NiCd)
# see: https://de.wikipedia.org/wiki/Tiefentladung
#       https://de.wikipedia.org/wiki/Entladeschlussspannung

UMIN = 1.00  # in Volts discharge low voltage
#UMIN = 1.10  # in Volts discharge low voltage for test purposes
DISCHARGE_INTERVAL = 5  #seconds


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


# CSV class to log discharge statistics
class DischargeCsv:

    def __init__(self, csv_file):
        self.logger = logging.getLogger('DischargeCsv')
        self.logger.debug("Class instantiated.")
        try:
            locale_name = 'de_DE.utf8'
#            locale_name = 'de_DE'
            locale.setlocale(locale.LC_ALL,locale_name)
        except locale.Error as e:
            self.logger.warning("Could not set locale for CSV file to <{0}>.".format(
                 locale_name))
            self.logger.warning("locale.setlocale() Error message: <{0}>".format(e))

        self.csv_writer = csv.writer(csv_file, delimiter=";")
        self.logger.debug("writing csv-header")
        self.csv_writer.writerow(["Time/sec","Ubat/V","Umin+/V", "Icurrent/mA",
             "Pcurrent/mW","TotalDischarge/mAh","TotalPower/mWh"])

    def write(self, tim, u_act, i_act, p_act, t_discharge, t_power):
        if self.csv_writer:
            self.logger.debug('csv-row: {0};{1:0.2f};{2:0.2f};{3:0.2f};{4:0.4f};{5:0.4f}'.format(
                           tim,u_act,u_act-UMIN,i_act,p_act,t_discharge,t_power))

            self.csv_writer.writerow([locale.format_string('%d',tim),
                                      locale.format_string('%0.4f',u_act),
                                      locale.format_string('%0.4f',u_act-UMIN),
                                      locale.format_string('%0.2f',i_act),
                                      locale.format_string('%0.2f',p_act),
                                      locale.format_string('%0.2f',t_discharge),
                                      locale.format_string('%0.2f',t_power)])
        else:
            self.logger.error("Class not properly initialized - no csv_writer object")


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


def print_start(lcd, uact,battery_low=False):
    logger = logging.getLogger("print_start")
    log_message("Discharge Meter - starting new measurement...")
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
    logger = logging.getLogger("print_status")
    logger.info(' Status: {0:6d} sec:  {1:5.3f} V  {2:7.2f} mA  {3:7.2f} mW  {4:8.2f} mAh  {5:8.2f}mWh'.format(
         tim,u_act,i_act,p_act,t_discharge,t_power))
#    print_display(lcd, 'Run     {0}\n{1:0.2f}V {2:0.0f}mA {3:0.0f}mAh '.format(duration_to_hhmmss(tim),
#         u_act,i_act,t_discharge))
    print_display(lcd, 'Running for {0}\n   {1:5.3f}V    {2:4.0f}mA\n   {3:5.0f}mAh {3:5.0f}mWh'.format(
         duration_to_hhmmss(tim),u_act,i_act,t_discharge, t_power))

def print_final(lcd, tim, discharge, power, voltage):
    logger = logging.getLogger("print_final")
    log_message('\n** Discharge duration: {0}\n** Total discharge:    {1:0.2f} mAh\n** Total energy:       {2:0.2f} mWh\n** Voltage:             {3:0.3f} V '.format(
         duration_to_hhmmss(tim), discharge, power, voltage))
    print_display(lcd, 'Done after {0}\nCapacity: {1:0.2f}mAh\nPower:    {2:0.2f}mWh\nVoltage:  {3:0.3f}V'.format(
         duration_to_hhmmss(tim), discharge, power, voltage))


# Main routine

if __name__ == "__main__":
    # Argument parsing
    parser = ArgumentParser(
             description='Discharge Meter - Discharges a battery while measuring'
             'voltage and current. Stops if voltage drops below minimum value.'
             )
    parser.add_argument('prefix', nargs='?', default="result",
                        help='Measurement prefix - taken for '
                        'the CSV amd log file name, default: "%(default)s".'
                       )
    parser.add_argument('-v', '--verbose', action='count', default=0,
                       help='Increase log level -vv is debug.')

    parser.add_argument('-t', '--timestamp', action='store_true',
                       help='Add timestamp after prefix for CSV file.')

    parser.add_argument('-l', '--log_output', action='store_true',
                       help='Logs output to file PREFIX-[TIMESTAMP].log.')

    parser.add_argument('-o', '--outfile',
                       help='Sets log file name. Overwrites -l option.')

    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite already existing files silently.')

    args = parser.parse_args()

    # Prepare logging and CSV file
    prefix = args.prefix
    files_overwrite = args.overwrite
    logfile = None
    logfile_name = None
    file_timestamp = ""

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

    if args.timestamp:
        today = datetime.now()
        file_timestamp = "-{0:4d}-{1:02d}-{2:02d}_{3:02d}{4:02d}".format(
                          today.year,today.month,today.day,today.hour,today.minute)

    if args.log_output:
        # Create log file name from prefix and optionally timestamp
        logfile_name = args.prefix + file_timestamp + ".log"
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


    csvfile_name = args.prefix + file_timestamp + ".csv"
    if check_would_overwrite(csvfile_name, files_overwrite):
        # Note what function above aborts for existing file and overwrite = False
        logger.warning("Overwriting existing CSV file <{0}>".format(csvfile_name))
    else:
        logger.info("Write discharge values to file {0}".format(csvfile_name))
    raw_csvfile = open(csvfile_name, "w")


    # Initialize peripheral hardware components

    # INA board
    i2c_bus = board.I2C()
    ina     = INA219(i2c_bus)
    ina219_init(ina)

    # electrical relay
    relay_io = digitalio.DigitalInOut(board.D17)
    relay_io.direction = digitalio.Direction.OUTPUT

    # OLED display
    # Luma compatible i2c and device objects
    i2cdev = i2c(port=1, address=0x3C)
    oled_font = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 10)
    lcd = OledSh1106(i2cdev, oled_font)
    lcd.greeting()

    # LCD display
#    lcd = character_lcd.Character_LCD_Mono(plcd.rs, plcd.en, plcd.d4, plcd.d5, plcd.d6, plcd.d7,
#               lcd_columns, lcd_rows, plcd.backlight, True)
#    lcd.clear()


    # Read initial battery voltage and start discharging while monitoring
    # voltage and current
    try:
        TotalDischarge = 0.0
        TotalPower = 0.0
        TimeDischarge = 0 # in seconds
        csv_last_uactual = csv_last_time = 0.0

        Uactual,Iactual,Pactual = ina219_read(ina)
        if Uactual <= UMIN:
            print_start(lcd, Uactual, battery_low=True)
            logger.info("Waiting 5 sec so before closing, so you can read the display")
            sleep(5)
        else:
            print_start(lcd, Uactual, battery_low=False)

            csvfile = DischargeCsv(raw_csvfile) # the class gets an file handle
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
            logger.info("Voltage difference to trigger new CSV entry: {0:0.4f}".format(csv_delta_u))

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

                # read new values
                Uactual,Iactual,Pactual = ina219_read(ina)

                print_status(lcd, TimeDischarge, Uactual, Iactual, Pactual, TotalDischarge,
                     TotalPower)
                # reduce number of rows in CSV file
                if (abs(csv_last_uactual - Uactual) > csv_delta_u) or ((TimeDischarge - csv_last_time )> 60):
                     logger.info("Adding new row to CSV file.")
                     csvfile.write(TimeDischarge, Uactual, Iactual, Pactual,TotalDischarge, TotalPower)
                     csv_last_uactual = Uactual
                     csv_last_time =  TimeDischarge

            log_message('Current battery voltage of {0:0.2f} V dropped below mimimum of {1:0.2f} V'.format(
                 Uactual, UMIN))
            logger.info("Adding new row to CSV file.")
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

            print_final(lcd, TimeDischarge, TotalDischarge, TotalPower, Uactual)
            logger.info("Waiting 5 sec so before closing, so you can read the display")
            sleep(5)

    except KeyboardInterrupt:
        log_message("Keyboard interrupt - while discharging! Last voltage: {0:0.3f}V".format(Uactual))
        print_display(lcd, "Interrupted....\n{0}  {1:0.2f} mAh\nVoltage:  {2:0.3f}V".format(duration_to_hhmmss(TimeDischarge),
             TotalDischarge, Uactual))
        sleep_time = 5
        logger.info("Waiting 5 sec so before closing, so you can read the display")
        sleep(5)

    finally:
    #    pass
        reset_gpio(relay_io)
        if hasattr(raw_csvfile, "close"):
            logger.info("Closing CSV file...")
            raw_csvfile.close()
        if hasattr(logfile, "close"):
            logger.info("Closing log file...")
            logfile.close()

