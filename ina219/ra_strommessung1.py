from ina219 import INA219, DeviceRangeError
from time import sleep

SHUNT_OHM = 0.1
MAX_STROMSTAERKE = 0.4
ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

dev read_ina219():
    try:
        Uges = ina.voltage() + ina.shunt_voltage()/1000
        print('Ubat   : {0:0.2f} V'.format(Uges))
        print('Iges   : {0:0.2f} mA'.format(ina.current()))
        print('Pges   : {0:0.2f} mW'.format(ina.power()))
        print('UShunt : {0:0.2f} V'.format(ina.shunt_voltage()))
    except DeviceRangeError as e:
        print("Stromstärke zu hoch.")

while 1:
    read_ina219()
    sleep(5)
