# DHT11 project
  Using the DHT11 sensor to read temperature and humidity via I2C and SPI
  see: https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/
  and: https://tutorials-raspberrypi.de/raspberry-pi-daten-thingspeak-loggen-auswerten/

  The DHT11 and DHT22 are low cost temperature and humidity sensors.
  You find them from various manufacturers like DEBO,
  JOY-IT (https://joy-it.net/de/) or Adafruit (https://www.adafruit.com/).
  The differences between these sensors are range, accuracy and query frequency.
  The protocol to talk to them is slightly different as well.

  This project uses the Adafruit CircuitPython library for Raspberry Pi.
  It only supports `python3` and not the standard pi python version 2.7 !!

  The python module is `adafruit_dht` (https://github.com/adafruit/Adafruit_CircuitPython_DHT).
  It is depends on CircuitPython (https://github.com/adafruit/circuitpython)
  A deprecated repository exist the DHT module for historical reasons:
  https://github.com/adafruit/Adafruit_Python_DHT).

  Adafruit_dht is based on Adafruit's basic IO library (module `digitalio`)
  that comes with the package.
  You can install the full Adafruit basic IO libarary following the instructions
  below:
  https://learn.adafruit.com/adafruit-io-basics-digital-output/python-setup
  The IO libarary is available on GitHub: https://github.com/adafruit/io-client-python.git
  
  The abstraction of the IO pins comes from a module named `board`
  Don't confuse this module with the dojo-board project
  (https://pypi.org/project/board/ and  https://github.com/tjguk/dojo-board).


## HW Setup

  Connect the `Allnet Temp and Humidity B24` to the Pi GPIO port:
  ```
    Sensor Pins:

       +----------------+
     --+ +5V            |
       |                |
     --+ GND            |
       |                |
     --+ IO             |
       +----------------+

    GPIO         ->   B24 Sensor
    --------------------------------    
    GND          ->   GND
    3.3V         ->   +5V
    GPIO 04 (07) ->   IO
  ```
  Note: the board already contains the pull-up resistor for the
        IO pin of the DHT11 module

## Installation

  You need to run this all under python3!
  CircuitPython does not support python 2.7 anymore.

  Install Adafruit CircuitPython DHT library:
  Pre-reqs that are part of the full Raspi OS, which you may need on a light
  install:
    ```
    sudo apt-get update
    sudo apt-get install build-essential python-dev python-openssl git
    sudo pip3 install --upgrade setuptools
    ```

  Adafruit CircuitPython DHT:
    ```
    sudo pip3 install adafruit-circuitpython-dht
    sudo apt-get install libgpiod2
    ```

## Code

  - dht-example.py
    Uses the modules `board` and `adafruit_dht` to display temp and humidity in
    an endless loop.

    Note: This program must be started with python3.
