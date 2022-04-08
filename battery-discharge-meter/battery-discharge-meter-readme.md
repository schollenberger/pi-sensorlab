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

  Relais board (from the sensor kit):
  Note that AZ-Delivery sells a similar relais board but the pins are arranged
  differently.
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

  As an alternative to the LCD display, 128x64 pixel OLED displays with the
  SSD1306 chip and I2C serial interface have been used as well.
  They connected to the same I2C bus as the INA219 board.
  !! Double check the VCC/GND pins. !! They are swapped on some displays.

  OLED Display:
  ```
    +--------------------------+
    |      o   o   o   o       |
    |      1   2   3   4       |
    |     GND VCC SCL SDA      |
    |                          |
    |  +---------------------+ |
    |  |                     | |
    |  |                     | |
    |  |                     | |
    |  +---------------------+ |
    +--------------------------+

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
      |           +--------0          |
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

  - Check that the relay is functioning
    The command:  
    `gpio write 0 1; sleep 1; gpio write 0 0`  
    This should turn the relay on and off again.
    You may need to execute:  
    `gpio mode 0 out `  
    To initialize the GPIO port.

## Code

  - `discharge-meter.py`
    Battery discharger measuring accumulated current and power, display
    current data on a LCD module and writing them to a CSV file.
    Stops after discharging below minimum discharge voltage.

  - `lcd-dimm.sh`
    Writes to the electrical relay GPIO port to dim the LCD display

  - `lcd-on.sh`
    Writes to the electrical relay GPIO port to turn the LCD display on again.

  - `battery_test.oled.py`
    Measures the battery's initial voltage and then applies the load, and
    measures voltage and current under load for a short period. After that
    it lets the battery recover and measures the voltage again.

## Results

  Some typical result values of the battery test for AA Alkaline batteries:
    ```
      Load current about 220 - 330 mA, depending on load voltage.
      Overall load resistor 4.5 - 4.9 Ohms (including wires and relay resistance)

      Status  | initial     |  load
      --------+-------------+---------------
      fresh   | 1.55-1.67 V | 1.45 - 1.55 V
              |             |
      medium  |             | 1.25 - 1.44 V
              |             |
      poor    |             | 0.90 - 1.24
              | 1.27 V      | 1.16 V
              |             |
      replace |             | < 0.8 V
    ```

  Measurement comparison INA219 vs. oscilloscope:
  CH1 10x 1V/div - INA Vin+ / Battery + directly
  CH2 10x 1V/div - INA Vin-
  Math  - CH1 - CH2

  Measurements recorded via single sweep 100ms/div, Trigger via CH4 connected
  to internal oscillator. Measurement
    ```
    Relative fresh Battery AA size:

                         |  Idle    |  Load    |
    ---------------------+----------+----------+
    Scope @ battery      |  1.57 V  |  1.43 V  |
    Scope @ INA Vin+     |  1.57 V  |  1.34 V  |
    Scope @ INA Vin-     |  1.55 V  |  1.24 V  |
    Scope Vin+ - Vin-    |    10 mV |   96  mV |
    INA Ubat (Vin + Ush) |  1.50 V  |  1.30 V  |
    INA Ushunt           | -0.01 mV |  26.2 mV |
    INA Iges             | -0.10 mA |   262 mA |
    INA Pges             |  0.00 mW |   330 mW |
    ```
