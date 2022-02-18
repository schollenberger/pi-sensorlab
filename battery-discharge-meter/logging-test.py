#!/usr/bin/python3

# Test logging feature for discharge-meter code

import sys
import os.path
from datetime import datetime
from time import sleep

from argparse import ArgumentParser
import logging
from logging.config import dictConfig

loglevel_message = 5
logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-14s %(levelname)-8s %(message)s'},

        'm': {'format':
              '%(asctime)-14s *** %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG},

        'msg': {'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'm',
                'level': loglevel_message}
        },

    loggers = {
        'message': {'handlers': ['msg'],
                    'level': loglevel_message}
        },

    root = {
        'handlers': ['h'],
        'level': logging.WARNING
        },
)

UMIN = 1.00  # in Volts discharge low voltage
#UMIN = 1.10  # in Volts discharge low voltage for test purposes
DISCHARGE_INTERVAL = 5  #seconds


def log_message(txt):
    msglogger = logging.getLogger("message")
    msglogger.log(loglevel_message, txt)
#    print(txt)
#    sys.stdout.flush()
#    if hasattr(logfile, "write"):
#        print(txt, file=logfile)
#        logfile.flush()

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

# CSV class to log discharge statistics
class DischargeCsv:

    def __init__(self, csv_file):
        logger = logging.getLogget(__name__)
        logger.debug("Class instantiated.")
        pass


    def write(self, tim, u_act, i_act, p_act, t_discharge, t_power):
        pass
        logger.info("record written timestamp = %s.", tim)


def ina219_read(ina219):
    logger = logging.getLogger("ina219_read()")
    logger.debug("Start reading ina board...")
    Uges = ina219
    Iina = 210.34
    logger.info("Read values from ina219: %0.2f V, %4.2f mA,  %4.2f mW", Uges, Iina, Iina * Uges)
    return Uges, Iina, Iina*Uges

####
def resetLogging():
    """ Reset the handlers and loggers so that we
    can rerun the tests starting from a blank slate.
    """
#    __pragma__("skip")
    logging._handlerList = []
    import weakref
    logging._handlers = weakref.WeakValueDictionary()
    logging.root = logging.RootLogger(logging.WARNING)
    logging.Logger.root = logging.root
    logging.Logger.manager = logging.Manager(logging.root)
    logging.root.manager = logging.Logger.manager
#    __pragma__("noskip")

#    if __envir__.executor_name == __envir__.transpiler_name:
#        logging._resetLogging()

"""
resetLogging()
dictConfig(logging_config)
logging.warning("Hello")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmt = logging.Formatter('--- %(levelname)s - %(message)s')
ch.setFormatter(fmt)
logging.root.addHandler(ch)

logging.warning("Hallo")
logging.info("Hallo")

"""
####


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
    logger.info("Log level =  %s.",
         logging.getLevelName(logging.root.getEffectiveLevel())
         )
    # Example of variable level logging
    # logger.log(logger.getEffectiveLevel(), 'Logging initialized - no file handler set yet.')

    # Process arguments for log level.
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

#        print(logging.root.handlers
#        logger.root.removeHandler(logging.root.handlers[0])
#        print(logging.root.handlers)

        ch = logging.root.handlers[0]
        ch.setLevel(logging.WARNING)

#        _fmt = logging.Formatter(logging_config['formatters']['m']['format'])
#        _handler = logging.StreamHandler(logfile)
#        _handler.setFormatter(_fmt)
#        msg_logger = logging.getLogger("message")
#        msg_logger.addHandler(_handler)

    csvfile_name = args.prefix + file_timestamp + ".csv"
    if check_would_overwrite(csvfile_name, files_overwrite):
        # Note what function above aborts for existing file and overwrite = False
        logger.warn("Overwriting existing CSV file <{0}>".format(csvfile_name))
    else:
        logger.info("Write discharge values to file {0} in CSV format.".format(csvfile_name))
    #raw_csvfile = open(csvfile_name, "w")


    # Initialize peripheral hardware components
    # ... skipped

    # Read initial battery voltage and start discharging while monitoring
    # voltage and current
    try:
        TotalDischarge = 0.0
        TotalPower = 0.0
        TimeDischarge = 0 # in seconds
        csv_last_uactual = csv_last_time = 0.0

        Uactual,Iactual,Pactual = ina219_read(1.4)
        sleep(5)
        log_message("Start discharging...")
        sleep(1)

        TimeDischarge  += 1
        Uactual,Iactual,Pactual = ina219_read(1.3)
        log_message("Voltage difference to trigger new CSV entry: 0.03 V")

        while Uactual > UMIN:

            sleep(DISCHARGE_INTERVAL)
            TimeDischarge  += DISCHARGE_INTERVAL
            TotalDischarge += Iactual * DISCHARGE_INTERVAL/3600
            TotalPower     += Pactual *  DISCHARGE_INTERVAL/3600
            Uactual,Iactual,Pactual = ina219_read(1.2)

    except KeyboardInterrupt:
        log_message("Keyboard interrupt - while discharging! Last voltage: {0:0.3f}V".format(Uactual))


    finally:
        pass
