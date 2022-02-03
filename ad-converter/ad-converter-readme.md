# AD-Converter Project
  Connect an MCP3008 AD converter to the SPI port of an Raspberry Pi.
  Examples with `Allnet Joystick B01`

## HW Setup
  MCP3008:
  See: https://tutorials-raspberrypi.de/raspberry-pi-mcp3008-analoge-signale-auslesen/
  Put this IC with the notch downside, so the pins facing the PI are on the
  left hand side.

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
  Joystick B01
  ```
    Sensor Pins:

       +----------------+
       |                |
       |                |
       |                |
     --+ +5V            |
       |                |
     --+ GND            |
       |                |
     --+ X              |
       |                |
     --+ Y              |
       |                |
     --+ BUT            |
       +----------------+
  ```

  The button has already a 2.2 kOhms pull-up resistor on the PCB.

  Connect the `Allnet Joystick B01` to the AD Converter:
  ```
    AD Channel ->   B01 Joystick
    ----------------------------
    CH0          ->   BUT
    CH1          ->   X
    CH2          ->   Y
  ```

## Install

  By default SpiDev is installed on a full Raspi OS
  Otherwise execute:
  ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-dev

    # download SpiDev library, unpack and install:

    wget https://github.com/doceme/py-spidev/archive/master.zip
    unzip master.zip
    cd py-spidev-master
    sudo python setup.py install
  ```


## Code

  - `MCP3008.py`
    Python class to include to abstract from the SpiDev library.
    Supports method: `read(channel)` - results a value between 0 and 4096
    (according to docs 1024).

  - `simple-read.sh`
    Read channel 0 and 1 periodically every second and convert to voltage.

  - `joystick_test.py`
    Read Joystick values
    wget http://www.tutorials-raspberrypi.de/wp-content/uploads/scripts/joystick_test.py
