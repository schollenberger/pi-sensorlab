#! /usr/bin/python
#
# Test program for lirc library - receive signals
# Note that the lircd service must be configured to support receiving signals.
#

import lirc
import time

def myexit_0(clt):
	print("... exiting closing the lirc client.")
	clt.close()
	exit()

def myexit_1(clt,conn):
	print("... exiting closing lirc client and connection.")
	conn.close()
	client.close()
	exit()

remote_name ="Panasonic_N2QAYB000124-DVD"
#remote_name ="TEST"
remote_key_exit ="KEY_POWER"
#remote_key_exit ="KEY_xx"

client = lirc.Client() # using default connection socket /var/run/lirc/lircd
print("Python lirc module version: " + client.version())

try:
	remotes = client.list_remotes()
	print("Supported remote controls:")
	found = False

	for remote in remotes:
		if remote == remote_name:
			found = True
			print(" - {0}   - used in this program.".format(remote))
		else:
			print(" - {0}".format(remote))

	if not found:
		print("Aborting - this program uses the remote control <{0}>".format(remote_name))
		print("           The remote is not supported by the lirc installation.")
		myexit_0(client)

	keys = client.list_remote_keys(remote_name)

	print("Keys for the remote {0}:".format(remote_name))
	found = False
	for key in keys:
		if remote_key_exit in key:
			found = True
			print(" - {0}   - used as exit key in this program.".format(key))
		else:
			print(" - {0}".format(key))

	if not found:
		print("Aborting - no exit key found")
		myexit_0(client)

except lirc.exceptions.LircdCommandFailureError:
	print("*Runtime ERROR* in executing method list_remote()/list_remote_keys on lirc.Client")
	client.close()
	exit(1)

print("Preparing to read remote keys...")
connection = lirc.LircdConnection()
connection.connect()

print("Now press keys on the remote - to exit press key {0} on remote {1}".format(remote_key_exit, remote_name))
key_read = ""

while remote_key_exit not in key_read:
	try:
		socket_read = connection.readline()
		print("Received : ", socket_read.split())
		key_read = socket_read.split()[2]
		print("Key read: ", key_read, " from remote", socket_read.split()[3])
		print()
	except TimeoutError:
		print("Timeout - continuing...  (Press Power button to end)")

print("...ending...")
connection.close()
client.close()

print()
print("Done...")
