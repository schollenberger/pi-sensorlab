from datetime import datetime
from ina219 import INA219, DeviceRangeError
from time import sleep


SHUNT_OHM = 0.1
#MAX_STROMSTAERKE = 0.4
MAX_STROMSTAERKE = 1.0

ina = INA219(SHUNT_OHM, MAX_STROMSTAERKE)
ina.configure(ina.RANGE_16V)
#ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)
#ina.configure(ina.RANGE_16V, ina.GAIN_2_80MV)
#ina.configure(ina.RANGE_16V, ina.GAIN_4_160MV)
#ina.configure(ina.RANGE_16V, ina.GAIN_8_320MV)

def read_ina219():
    try:
        Ushunt = ina.shunt_voltage()
        Uina = ina.voltage()
        Iina = ina.current()
        Pina = ina.power()
        Uges = Uina + Ushunt/1000
        '''
        print('Ubat   : {0:0.2f} V'.format(Uges))
        print('Iges   : {0:0.2f} mA'.format(Iina))
        print('Pges   : {0:0.2f} mW'.format(Pina))
        print('UShunt : {0:0.2f} mV'.format(Ushunt))
        print()
        '''
        return Iina, Uina, Pina, Ushunt
    except DeviceRangeError as e:
        print("Stromstaerke zu hoch.")
        print(e)

# Main

try:

   print("INA219 read test")
   print("Initial reading:")

   (Iina, Uina, Pina, Ushunt) = read_ina219()

   print('Uina   : {0:0.2f} V'.format(Uina))
   print('Iges   : {0:0.2f} mA'.format(Iina))
   print('Pges   : {0:0.2f} mW'.format(Pina))
   print('UShunt : {0:0.2f} mV'.format(Ushunt))
   print()

   Itotal = 0.0
   Ipast = 0.0
   Isum = Iina
   Ipeak = Iina
   delay = 0.2
   count = 1

   while 1:
        (Iina, Uina, Pina, Ushunt) = read_ina219()

        sleep(delay)

        ts = datetime.now()
        Itotal = Itotal + Iina * delay/3600
        Isum = Isum + Iina
        if abs(Iina) > abs(Ipeak):
             Ipeak = Iina
        if count % 10 == 0:
             Iavg = Isum/(count + 1)
             print('{} - U: {:6.3f} V - Iact: {:8.2f} mA - Total: {:10.6f} mAh - Iavg: {:8.2f} mA - Ipeak: {:8.2f}'.format(
                    ts, Uina - Ushunt/100, Iina, Itotal, Iavg, Ipeak))
             Ipast = Itotal
             Isum = Iina
             Ipeak = Iina
             count = 0
        count += 1


except KeyboardInterrupt:
    pass
    print
    print("That's all folks ...")
