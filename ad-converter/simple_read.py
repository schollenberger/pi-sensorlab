#!/usr/bin/python
import time
from MCP3008 import MCP3008

adc = MCP3008()

chan0 = 0  # auszulesender channel
chan1 = 1
chan2 = 2

uref = 3.3

ad_range = 4095.0

val0 = adc.read(chan0)
val1 = adc.read(chan1)
val2 = adc.read(chan2)
#print("Anliegende Spannung: %.2f Volt" % (value / 4096.0 * 3.3) )
#print("Anliegende Spannung: %.6d " % value  )
print("AD-Wandler MCP3008 - Leseschleife")
print("Referenzspannung:    {0:.4f} V".format(uref))
print("Aufloesung:          {0:.6f} V".format(uref / ad_range))
print("Ausgelesene Channel: %i, %i, %i" % (chan0, chan1 , chan2))

try:
    while 1:
        val0 = adc.read(chan0)
        val1 = adc.read(chan1)
        val2 = adc.read(chan2)

        print("Anliegende Spannung: %.4f / %.4f / %.4f Volt - Raw values:  %5d / %5d / %5d " % (
           (val0 * uref / ad_range), (val1 * uref / ad_range),  (val2 * uref / ad_range), val0, val1, val2))
        time.sleep(1)

except KeyboardInterrupt:
    pass
