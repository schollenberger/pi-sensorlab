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
    HD44780 1602 (2x16 char)
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

    HD44780 2004 (4x20 char) - electrical compatiple with module above
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
    |  | <Third line>                                               | |
    |  | <Fourth line>                                              | |
    |  +------------------------------------------------------------+ |
    +-----------------------------------------------------------------+

  ```

  For parallel IO, connect Module the following (you need 8 wires in total).
  However, this setup requires to configure the module to 4-bit mode (but
  this is standard with the Adafruit-CharLCD python module):

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

## Usage
  Using parallel IO the Pi controls the LCD module interface directly using
  6 GPIO ports.
  There are several Adafruit-CharLCD libraries on GitHub:
     https://github.com/adafruit/Adafruit_Python_CharLCD/tree/master/Adafruit_CharLCD
     https://github.com/born2net/raspberry/tree/master/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCD
     https://github.com/codecube/raspberry-pi-GPIO/blob/master/Adafruit_CharLCD.py

  The one that get installed via the pip command above is:
     https://github.com/adafruit/Adafruit_Python_CharLCD/
  Note, that it is deprecated and Adafruit wants you to use the CircuitPython
  version.

  This library can be used to initializes the LCD module, clear the display and
  write messages to it.
  To split messages running over several lines, you can use the newline ('\n')
  character. However the 4x20 module doesn't behave as expected. On this
  module the characters beyond column 19 of line 1 appear on the 3rd line.
  You cannot address the 3rd and 4th line via newline characters using this
  module.
  One solution to this is to use python string formatting like in the following
  example:
  ```
    "{0:20s}{2:20s}{1:20s}{3:20s}".format("Line1","Line2","Line3","Line4")
  ```


## Code

  - `lcd-simple-2x16.py`
    From https://www.rototron.info/raspberry-pi-ina219-tutorial/
    It uses the deprecated Adafruit-CharLCD library.

  - `lcd-simple-4x20.py`
    Derived from `lcd-simple-2x16.py`.
    It uses the deprecated Adafruit-CharLCD library.
 
