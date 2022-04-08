# From: https://github.com/adafruit/Adafruit_CircuitPython_INA219/blob/main/examples/ina219_simpletest.py
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Sample code and test for adafruit_ina219"""

import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219


i2c_bus = board.I2C()

ina219 = INA219(i2c_bus)

print("ina219 test")

# display some of the advanced field (just to test)
print("Config register (default state):")
print("  bus_voltage_range:    0x%1X" % ina219.bus_voltage_range)
print("  gain:                 0x%1X" % ina219.gain)
print("  bus_adc_resolution:   0x%1X" % ina219.bus_adc_resolution)
print("  shunt_adc_resolution: 0x%1X" % ina219.shunt_adc_resolution)
print("  mode:                 0x%1X" % ina219.mode)
print("")

# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
#ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
#ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

ina219.gain = 0                   # 1 - +- 40 mV
#ina219.gain = 1                   # /2 - +- 80 mV
#ina219.gain = 3                   # /8 - +- 320 mV

#ina219.bus_adc_resolution = 12    # 16 samples 8.51 ms
ina219.bus_adc_resolution = 15    # 128 samples 68.101 ms

#ina219.shunt_adc_resolution = 12
ina219.shunt_adc_resolution = 15

# display some of the advanced field (just to test)
print("")
print("Config register (initialized):")
print("  bus_voltage_range:    0x%1X" % ina219.bus_voltage_range)
print("  gain:                 0x%1X" % ina219.gain)
print("  bus_adc_resolution:   0x%1X" % ina219.bus_adc_resolution)
print("  shunt_adc_resolution: 0x%1X" % ina219.shunt_adc_resolution)
print("  mode:                 0x%1X" % ina219.mode)
print("")

# measure and display loop

while True:
    bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina219.current  # current in mA
    power = ina219.power  # power in watts

    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    print("Voltage (VIN+) : {:8.5f} V".format(bus_voltage + shunt_voltage))
    print("Voltage (VIN-) : {:8.5f} V".format(bus_voltage))
    print("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
    print("Shunt Current  : {:8.2f} mA".format(current))
    print("Power Calc.    : {:8.2f} mW".format(bus_voltage * current))
    print("Power Register : {:6.3f}   W".format(power))
    print("")

    # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if ina219.overflow:
        print("Internal Math Overflow Detected!")
        print("")

    time.sleep(2)
