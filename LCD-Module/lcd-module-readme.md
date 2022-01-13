# AZ-Delivery LCD Module Project
  Drive AZ-Delivery LCD module via Raspberry Pi IO pins and I2C bus.

  This project contains the HW set up and some sample code to drive the
  AZ-Delivery LCD modules HD44780-2001 (2x16 chars) and HD44780-2001 (4x20 chars).
  AZ-Delivery provides and I2C-adapter to drive the modules, in order to
  save IO-Pins. This project contains the HW setup in conjunction with this
  I2C-adapter as well.

  The AZ-Delivery LCD module requires 5 V supply but tolerates the 3.3 V levels
  from the PI's GPIO board for its control and data lines.
  So if you connect the module directly to GPIO pins no level shifter is needed.
  But if you use the I2C-adapter you must place a level shifter between the
  Signals of the Pi and the I2C-controller.

## Link to the Tutorial I followed:
  https://

## HW Setup HD44780
  Details on  Dot-Matrix LCD Displays of type HD44780
     http://www.sprut.de/electronic/lcd/
     https://www.mikrocontroller.net/articles/HD44780
  Both HD44780 LCD modules have the same pin layout.

  ```
    +-----------------------------------------------------------------+
    |  +------------------------------------------------------------+ |
    |  |                                                            | |
    |  |                                                            | |
    |  +------------------------------------------------------------+ |
    |                                                                 |
    |           Cathode  Anode                    Enable              |
    |                 |  |                          |        C VCC GND|
    |                 K  A D7 D6 D5 D4 D3 D2 D1 D0  E RW RS V0 VDD VSS|
    |                 o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  o  |
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
  With the connection setup from above the LCD module runs in 4-bit mode

## Install

  The stuff below might already be installed on a full Raspi OS.
  Otherwise execute:
  ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-dev
    sudo apt-get install i2c-tools

    sudo pip install Adafruit-CharLCD # Python LCD module support on PI
    sudo pip install Adafruit-GPIO    #
  ```

## Check setup

  - Check I2C bus on PI
       sudo i2cdetect -y 1



## Code

  - `ra_strommessung1.py`
    From https://www.rahner-edu.de/raspberry-pi/strom-messen-mit-ina219/

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
        | +        | |                  |
       -+-         | |                  |
     ---+---       +++                  |
        | -         |                   |
        |           |                   |
        +-----------+-------------------+
    ```
