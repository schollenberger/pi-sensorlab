#!/usr/bin/python
#
# Works on both Python2 and Python2

from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import *
from time import sleep, strftime
from datetime import datetime

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=25, d7=24,
                       cols=16, lines=2)

cmd_eth  = "ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"
cmd_wlan = "ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"

#lcd.begin(16, 1)

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    if not isinstance(output, str):
         output = output.decode("utf-8")
    return str(output)


ipaddr = run_cmd(cmd_eth)
if len(ipaddr) == 0:
#   ipaddr = run_cmd(cmd_wlan).rstrip("\n")
   ipaddr = run_cmd(cmd_wlan)

ipaddr = ipaddr.rstrip("\n")
print("IP address: {0}".format(ipaddr))
print("Check running clock and IP address on LCD display")
try:
    while 1:
        lcd.clear()
        lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
        lcd.message('IP: %s' % (ipaddr))
        sleep(2)
except KeyboardInterrupt:
    pass

lcd.clear()
print()
print("That's all folks ...")

