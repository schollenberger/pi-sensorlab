#!/bin/bash

if [ -z "$1" ]; then
  _delay=5
elif [ "$1" == "-h" ]; then
 echo "toggle-led.sh  [<duraton> | -h]"
 exit
else
 _delay=$1
fi

gpio export 17 out
gpio export 27 out
gpio export 22 out

gpio -g write 17 0
gpio -g write 27 0
gpio -g write 22 0

echo "Starting with dark LED ..."
sleep $_delay
i=3
while [[ $i -ge 0 ]]; do
  echo "$i - LED red - green - blue ..."
  gpio -g write 22 1
  sleep $_delay
  gpio -g write 22 0
  gpio -g write 27 1
  sleep $_delay
  gpio -g write 27 0
  gpio -g write 17 1
  sleep $_delay
  gpio -g write 17 0
  ((i--))
done

echo "That's all folks ..."


