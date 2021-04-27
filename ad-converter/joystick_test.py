#!/usr/bin/python

import spidev
import os
import time

# Definiere Achsen Channels
# (channel 3 bis 7 koennen fuer weitere Tasten/Joysticks
# vergeben werden)
swt_channel = 0
vrx_channel = 1
vry_channel = 2

# Zeitverzoegerung, alle wie viel Sekunden ausgelesen wird
delay = 0.5

# Spi oeffnen
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Funktion zum auslesen des MCP3008
# channel zwischen 0 und 7
def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data


# Endlosschleife
while True:

  # Position bestimmen
  vrx_pos = readChannel(vrx_channel)
  vry_pos = readChannel(vry_channel)

  # SW bestimmen
  swt_val = readChannel(swt_channel)

  # Ausgabe
  print("VRx : {}  VRy : {}  SW : {}".format(vrx_pos,vry_pos,swt_val))

  # Warten
  time.sleep(delay)
