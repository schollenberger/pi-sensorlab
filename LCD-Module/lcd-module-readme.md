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

    sudo pip install Adafruit-GPIO    #

    sudo pip install Adafruit-CharLCD # deprecated Python LCD module support
  ```

   The CharLCD library that Adafruit supports is based on CircuitPython and can
   be found under:
      https://github.com/adafruit/Adafruit_CircuitPython_CharLCD
   You need to have Python3 as the default and Blinka installed (See install
   memos.)

   Once you satisfy the Blinka pre-req, install the CharLCD module as follows:
   ```
      pip3 install adafruit-circuitpython-charlcd
   ```
   That satisfies the following imports:
   ```
     import board
     import digitalio
     import adafruit_character_lcd.character_lcd as character_lcd
   ```

## Usage
  Using parallel IO the Pi controls the LCD module interface directly using
  6 GPIO ports.
  There are several python based Adafruit-CharLCD libraries on GitHub:
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

  The CircuitPython based CharLCD library is documented under:
     https://github.com/adafruit/Adafruit_CircuitPython_CharLCD
     https://circuitpython.readthedocs.io/projects/charlcd/en/latest/

  It works the following way:

    - Imports:
      ```
        import board
        import digitalio
        import adafruit_character_lcd.character_lcd as character_lcd
      ```

    - Define LCD display GPIO ports:
      ```
        lcd_rs = digitalio.DigitalInOut(board.D21)
        lcd_en = digitalio.DigitalInOut(board.D20)
        lcd_d7 = digitalio.DigitalInOut(board.D16)
        lcd_d6 = digitalio.DigitalInOut(board.D12)
        lcd_d5 = digitalio.DigitalInOut(board.D7)
        lcd_d4 = digitalio.DigitalInOut(board.D8)
        # lcd_backlight = digitalio.DigitalInOut(board.D13)
      ```

    - Specify display dimensions:
       ```
         lcd_columns = 16
         lcd_rows = 2
       ```
    - Create display object:
        `lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5,
                 lcd_d6, lcd_d7, lcd_columns, lcd_rows) # leaving out  lcd_backlight`

    - It is a good idea to move the IO port assignment to a separate module
      and reference them when creating the lcd object.

## Code

  - `lcd-simple-2x16.py`
    From https://www.rototron.info/raspberry-pi-ina219-tutorial/
    It uses the deprecated Adafruit-CharLCD library.

  - `lcd-simple-4x20.py`
    Derived from `lcd-simple-2x16.py`.
    It uses the deprecated Adafruit-CharLCD library.

  - `ipclock-example.py`
    From: https://github.com/born2net/raspberry/blob/master/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCD/Adafruit_CharLCD_IPclock_example.py
    It required some modifications to show the correct IP connected via WIFI.

  - `lcd-clear.py`
    Just to clear the display - uses the deprecated python LCD library.

  - `lcd_circuit_ports.py`
    Module which defines the custom IP ports to control the display.
    It gets imported into the other examples that use the Circuit library.

  - `lcd_circuit_example-4x20.py`
    Example code for how to use the Circuit library.

  - `charlcd_custom_character_nyan_cat.py`
    From https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/tree/main/examples
    Adapted to custom GPIO settings importing `lcd_circuit_ports`.

  - `charlcd_customcharacter.py`
    From https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/tree/main/examples
    Adapted to custom GPIO settings importing `lcd_circuit_ports`.
