# INA219 Voltage/Current Measurement Project
  Measure voltage and current via an AdaFruit INA 219 breakout board connected
  to a Raspberry Pi.
  This INA219 chip uses the I2C bus (SCL/SDA) to communicate.

  See the Pi-General-Memo document on how this board works and for tutorial
  links.

## Link to the Tutorial I followed:
  https://www.rototron.info/raspberry-pi-ina219-tutorial/

## HW Setup
  INA219 Board:

  ```
    +--------------------------------+
    |                                |
    |   o    o    o    o    o    o   |
    | Vin+ Vin-  Sda  Scl  Gnd  Vcc  |
    |                                |
    |                                |
    |       +------------+           |
    |       |   O    O   |           |
    |       | Vin-  Vin+ |           |
    |       +------------+           |
    |                                |
    +--------------------------------+

  ```

  Connect AD converter the following:

  ```
    RasüberryPi     ->  INA219 Board
    ---------------------------------
    Pin 1 (3.3V)    ->  Vcc
    Pin 3 (GPIO 02) ->  Sda
    Pin 5 (GPIO 03) ->  Scl
    Pin 6 (GND)     ->  Gnd

  ```    

## Install

  The stuff below might already be installed on a full Raspi OS.
  Otherwise execute:
  ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-dev
    sudo apt-get install i2c-tools

    sudo pip install pi-ina219        # Python INA219 support on PI
    sudo pip install Adafruit-PureIO  # .
    sudo pip install Adafruit-GPIO    #
  ```

  As an alternative to `pi-ina219` you may want to install the AdaFruit
  CircuitPython library which works in conjuction with AdaFruit's Blinka module
  and Python3 only.
  To install this module execute:
  ```
    pip3 install adafruit-circuitpython-ina219
  ```

## Check setup

  - Check I2C bus on PI
       sudo i2cdetect -y 1



## Code

  - `ra_strommessung1.py`
    From https://www.rahner-edu.de/raspberry-pi/strom-messen-mit-ina219/

  - `ina219_simpletest.py`
    Uses the Adafruit CircuitPython ina219 library and prints out the basic
    ina219 values.

  - `battery_measure.py`
    Simple battery discharger measuring accumulated current and power.
    Stops after discharging below minimum discharge voltage.
    There is a different project for a discharger with LCD display.
    Wiring Diagram:
    ```

                                           +-------------+
        +--------------------+             |   ina960    |
        |                    |             +-------------+
        |                    +-------------+-- Vin+      |
        |                                  |             |
        |                    +-------------+-- Vin-      |
        |                    |             |             |
        |  +-----------------+----+     +--+-- GND       |
        |  |          +++    |+ | |     |  +-------------+
        |  |  Relais  +++===>  |  |     |
        |  |          +++     |   |     |
        |  |                 |    |     |
        |  +-----------------+----+     |
        |           +--------+          |
        |           |                   |
        |          +++                  |
        | +        | |   Discharge      |
       -+-         | |   Resistor       |
     ---+---       +++    ~ 4 Ohms      |
        | -         |                   |
        |           |                   |
        +-----------+-------------------+
    ```
