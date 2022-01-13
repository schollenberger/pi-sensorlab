from ina219 import INA219, DeviceRangeError
import RPi.GPIO as GPIO
from time import sleep

# discharge low voltage = 1.0 V (NiMH) / 0.85 - 1 V (NiCd)
# see: https://de.wikipedia.org/wiki/Tiefentladung
#       https://de.wikipedia.org/wiki/Entladeschlussspannung

SHUNT_OHM = 0.1
MAX_STROMSTAERKE = 0.4
RELAY_IO = 17
UMIN = 1.05  # Volts discharge low voltage
#UMIN = 1.09  # Volts discharge low voltage for test purposes
DISCHARGE_INTERVAL = 5  #seconds

ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_IO,  GPIO.OUT)

def read_ina219():
    try:
        Ushunt = ina.shunt_voltage()
        Uina = ina.voltage()
#        Uges = Uina
        Uges = Uina + Ushunt/1000
        Iina = ina.current()
        Pina = ina.power()
        print('Ubat/I/P: {0:0.4f} V  / {1:0.4f} mA / {2:0.4f} mW - calculated P {3:0.4f} mW'.format(Uges,Iina,Pina,Iina*Uges))
        # print('Pges   : {0:0.2f} mW'.format(Pina))
        # print('UShunt : {0:0.2f} mV'.format(Ushunt))
        print
    except DeviceRangeError as e:
        print("Stromstaerke zu hoch.")
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
    print('-- {0} sec: Entladung: {1:0.6f} mAh  Energie: {2:0.6f} mWh'.format(tim, discharge, power))

def print_final(tim, discharge, power):
    print('Dauer: {0} min - Entladung: {1:0.4} mAh  Energie: {2:0.4f} mWh'.format(tim/60, discharge, power))


try:
    TotalDischarge = 0.0
    TotalPower = 0.0
    TimeDischarge = 0 # in seconds

    Uactual,dummy,dummy = read_ina219()
    if Uactual <= UMIN:
        print('Batterie / Akku hat eine zu geringe Spannung: {0:0.2f} V'.format(Uactual))
    else:
        print('Initiale Spannung: {0:0.2f} V'.format(Uactual))
        print("Beginne mit der Entladung...")
        turn_on()
        print_status(0, TotalDischarge, TotalPower)
        while Uactual > UMIN:
            Uactual,Iactual,Pactual = read_ina219()
            sleep(DISCHARGE_INTERVAL)
            TimeDischarge  += DISCHARGE_INTERVAL
            TotalDischarge += Iactual * DISCHARGE_INTERVAL/3600
            TotalPower     += Pactual *  DISCHARGE_INTERVAL/3600
            print_status(TimeDischarge, TotalDischarge, TotalPower)
        print('Entladeschlussspannung unterschritten -  Batterie/Akku-Spannung: {0:0.2f} V'.format(Uactual))
        print('Beende Entladung...')
        turn_off()
        sleep(1)
        Uactual,dummy,dummy = read_ina219()
        print('Spannung nach Ladeschluss: {0:0.2f} V'.format(Uactual))
        print_final(TimeDischarge, TotalDischarge, TotalPower)
    reset_gpio()

except KeyboardInterrupt:
    pass
    reset_gpio()
    print
    print("Keyboard interrupt - while discharging  ...")
    print('Dauer: {0} min - Entladung: {1:0.6f} mAh  Energie: {2:0.6f} mWh'.format(TimeDischarge/60, TotalDischarge, TotalPower))
