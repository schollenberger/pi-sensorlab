# Battery Discharge Meter Project
  This project is a about using the Raspberry Pi to measure voltage and
  current while discharging a battery.

  Measuring voltage and current is done via the AdaFruit INA 219 breakout
  board, an electircal relay board, a 2x16 char LCD display from AZ-Delivery
  and a battery holder with discharge resistor.

  It uses the I2C bus for the INA board and parallel IO to drive the display.


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

  Connect the INA board like the following:

  ```
    RasüberryPi     ->  INA219 Board
    ---------------------------------
    Pin 1 (3.3V)    ->  Vcc
    Pin 3 (GPIO 02) ->  Sda
    Pin 5 (GPIO 03) ->  Scl
    Pin 6 (GND)     ->  Gnd

  ```    

  Relais board:

  ```
    +------------------+
    |  +-------------+ |
    |  | NC   C  ACT | |
    |  |  o   o   o  | |
    |  +-------------+ |
    |   +-----------+  |
    |   |  \        |  |
    |   |   \       |  |
    |   |     0     |  |
    |   +-----------+  |
    |       5V  GND TTL|
    |        o   o   o |
    +------------------+
  ```

  Relais board connections

  ```
  RasüberryPi     ->  Relais Board
  ---------------------------------
  Pin 2 (5.0V)    ->  5V
  Pin 9 (GND)     ->  GND
  Pin11 (GPIO 17) ->  TTL
  ```

  LCD Module:
  ```
    +-----------------------------------------------------------------+
    |                                                                 |
    |   o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  o                |
    | VSS VDD V0 RS RW E  D0 D1 D2 D3 D4 D5 D6 D7 A  K                |
    |                  |                          |  |                |
    |               Enable                    Anode  Cathode          |
    |                                                                 |
    |  +------------------------------------------------------------+ |
    |  | <First line>                                               | |
    |  | <Second line>                                              | |
    |  +------------------------------------------------------------+ |
    +-----------------------------------------------------------------+

    V0 / C - Contrast voltage use 10 kOhm potentiomenter between GND and VCC
             to regulate or connect via 4.7 kOhm resistor to GND.
             The voltage on this pin should be arout 0.3 - 1.0 V.
    RS     - Register select (0 = command register, 1 = data register)
    RW     - Read/Write, may be set to GND write only mode and busy waiting
    E      - Clock / Enable - no internal pull-up!
    A      - Anode of LED backlight (connect via 100 Ohms to +5V)
    K      - Cathode of LED backlight (connect to GND)
  ```

  For parallel IO, connect Module the following (you need 8 wires in total):

  ```
    RasüberryPi     ->  LCD Module
    ---------------------------------

    Pin 2 (5.0V)    ->  VDD/VCC
                    ->  [Resistor 51 /100 Ohms]  -> A / Anode

    Pin14 (GND)     ->  VSS/GND, RW. K/Cathode
                    ->  [Resistor 4.7 kOhms]  -> C / V0
    Pin24 (GPIO 08) ->  D7
    Pin26 (GPIO 07) ->  D6
    Pin32 (GPIO 12) ->  D5
    Pin36 (GPIO 16) ->  D4
    Pin38 (GPIO 20) ->  E
    Pin40 (GPIO 21) ->  RS

  ```

  AD converter MCP3008:

  ```

               +-----------+
        DGND --+  9      8 +-- CH7
     CS/SHDN --+ 10      7 +-- CH6
         Din --+ 11      6 +-- CH5
        Dout --+ 12      5 +-- CH4
         CLK --+ 13      4 +-- CH3
        AGND --+ 14      3 +-- CH2
        Vref --+ 15      2 +-- CH1
         Vdd --+ 16  xx  1 +-- CH0
               +-----------+
  ```

  Connect AD converter the following:

  ```
    RaspberryPi    ->  MCP3008
    --------------------------------
    Pin 1 (3.3V)   ->  Pin 16 VDD
    Pin 1 (3.3V)   ->  Pin 15 Vref
    Pin 6 (GND)    ->  Pin 14 AGND
    Pin 23 (SCLK)  ->  Pin 13 (CLK)
    Pin 21 (MISO)  ->  Pin 12 (Dout)
    Pin 19 (MOSI)  ->  Pin 11 (Din)
    Pin 24 (CE0)   ->  Pin 10 (CS/SHDN)
    Pin 6 (GND)    ->  Pin  9 (DGND)


  ```    

  Complete setup (w/o display):
  ```
                                              +--------------+
                           0------------------+-- CH0        |
                           |                  |              |
                           |                  | AD-Converter |
                           |                  |              |
      +--------------------+          +-------+-- AGND       |
      |                    |          |       +--------------+
      |                    +---------------+
      |                               |    |  +-------------+
      |                    +-------------+ |  |   ina960    |
      |                    |          |  | |  +-------------+
      |  +-----------------+----+     |  | +--+-- Vin+      |
      |  |          +++    |+ | |     |  |    |             |
      |  |  Relais  +++===>  |  |     |  +----+-- Vin-      |
      |  |          +++     |   |     |       |             |
      |  |                 |    |     +-------+-- GND       |
      |  +-----------------+----+     |       +-------------+
      |           +--------o          |
      |           |                   |
      |          +++                  |
      | +        | |   Discharge      |
     -+-         | |   Resistor       |
   ---+---       +++    ~ 4 Ohms      |
      | -         |                   |
      |           |                   |
      +-----------+--------0----------+
  ```


## Install

  The stuff below might already be installed on a full Raspi OS.
  Otherwise execute:
  ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-dev
    sudo apt-get install i2c-tools

    # Install AdaFruit Blinka - see as well the Pi Installations document.
    cd ~
    sudo pip3 install --upgrade adafruit-python-shell
    wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
    sudo python3 raspi-blinka.py
    # -> you have to reboot

    pip3 install adafruit-circuitpython-ina219
    pip3 install adafruit-circuitpython-charlcd

    # download SpiDev library, unpack and install:
    wget https://github.com/doceme/py-spidev/archive/master.zip
    unzip master.zip
    cd py-spidev-master
    sudo python setup.py install

    # The lines below may be outdated as the newer code versions
    # in this project use the AdaFruit CircuitPython libraries which
    # are the only ones AdaFruit still supports.

    sudo pip install pi-ina219        # Python INA219 support on PI
    sudo pip install Adafruit-PureIO  # .
    sudo pip install Adafruit-GPIO    #
    sudo pip install Adafruit-CharLCD # Python LCD module support on PI

  ```

## Check setup

  - Check I2C bus on PI
       sudo i2cdetect -y 1


## Code

  - `discharge-meter.py`
    Battery discharger measuring accumulated current and power, display
    current data on a LCD module and writing them to a CSV file.
    Stops after discharging below minimum discharge voltage.

  - lcd-dimm.sh
    Writes to the electrical relay GPIO port to dim the LCD display

  - lcd-on.sh
      Writes to the electrical relay GPIO port to turn the LCD display on again.
