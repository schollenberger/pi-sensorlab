#! /usr/bin/python
#
# Test program for lirc library - send signals
# Note that the lircd service must be configured to support sending signals.
#

import lirc
import time

remote_name="Panasonic_N2QAYB000124-DVD"
remote_key1="KEY_1"
remote_key_slow="SEARCH>>"

client = lirc.Client() # using default connection socket /var/run/lirc/lircd
print("Python lirc module version: " + client.version())

try:
	print("Sending out button {1}  for remote control {0}".format(remote_name, remote_key1)) 
	client.send_once(remote_name, remote_key1)

	time.sleep(2)
	count=10

	print("Sending out {2} times button {1}  for remote control {0}".format(remote_name, remote_key1,count)) 
	client.send_once(remote_name, remote_key1, count)

	print ("Waiting a bit ...")
	time.sleep(3)

	duration=5
	print("Sending button {1} for {2} seconds for remote control {0}".format(remote_name, remote_key_slow,duration)) 
	client.send_start(remote_name, remote_key_slow)
	time.sleep(duration)
	client.send_stop()

except lirc.exceptions.LircdCommandFailureError:
	print("*Runtime ERROR* - One of the lirc.Client.send commands failed - be sure that the lircd serivce supports sending")


client.close()
print("Done...")
