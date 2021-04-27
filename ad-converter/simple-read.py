#!/usr/bin/python
import time
from MCP3008 import MCP3008

adc = MCP3008()

chan0 = 0  # auszulesender channel
chan1 = 1
chan2 = 2

val0 = adc.read(chan0)
val1 = adc.read(chan1)
val2 = adc.read(chan2)
#print ("Anliegende Spannung: %.2f Volt" % (value / 4096.0 * 3.3) )
#print ("Anliegende Spannung: %.6d " % value  )
print ("Lese channel %i, %i und %i  periodisch aus:" % (chan0, chan1 , chan2) )

try:
    while 1:
        val0 = adc.read(chan0)
        val1 = adc.read(chan1)
        val2 = adc.read(chan2)

        print ("Anliegende Spannung: %.2f / %.2f / %.2f Volt" % ((val0 / 4096.0 * 3.3), (val1 / 4096.0 * 3.3),  (val2 / 4096.0 * 3.3)))
        time.sleep(1)

except KeyboardInterrupt:
    pass
