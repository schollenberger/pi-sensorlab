from ina219 import INA219, DeviceRangeError
from time import sleep

SHUNT_OHM = 0.1
MAX_STROMSTAERKE = 0.4
ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

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

try:
    while 1:
        read_ina219()
        sleep(5)

except KeyboardInterrupt:
    pass
    print
    print("That's all folks ...")
