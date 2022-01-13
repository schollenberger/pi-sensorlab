# Battery Discharge Meter Project
  This project is a about using the Raspberry Pi to measure voltage and
  current while discharging a battery.

  Measuring voltage and current is done via the AdaFruit INA 219 breakout
  board, a relais board, a 2x16 char LCD display from AZ-Delivery and a
  battery holder with discharge resistor.

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

  Complete setup (w/o display):
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
