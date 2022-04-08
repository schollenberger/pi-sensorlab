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

  Connect INA219 board the following:

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
  CircuitPython library which works in conjunction with AdaFruit's Blinka module
  and Python3 only.
  To install this module execute:
  ```
    pip3 install adafruit-circuitpython-ina219
  ```

## Check setup

  - Check I2C bus on PI
       sudo i2cdetect -y 1

## Usage

### INA Libraries
  The `pi-ina219` library doesn't support triggered read operations. Not sure if
  the Adafruit library does.
  The `pi-ina219`library exports the module `ina219` while the AdaFruit library
  which has been programmed closer to the Adruino version exports the
  module `adafruit_ina219`.
  Both libraries contain a class named `INA219`, so this may lead to some
  confusion. However they need different supplement classes.

  Docs for `pi-ina219`:
    - https://pypi.org/project/pi-ina219/
    - In a nutshell:
        ```
        # imports
        from ina219 import INA219
        from ina219 import DeviceRangeError

        # initialization
        ina = INA219(SHUNT_OHMS) # simple auto-gain settings
        # or with more control
        ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=0x41, log_level=logging.INFO)
        ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV) # as an example

        # get the data
        print("Bus Voltage: %.3f V" % ina.voltage())
        try:
          print("Bus Current   : %.3f mA" % ina.current())
          print("Power         : %.3f mW" % ina.power())
          print("Supply Voltage: %.3f mW" % ina.supply_voltage())
          print("Shunt voltage : %.3f mV" % ina.shunt_voltage())
        except DeviceRangeError as e:
          # Current out of device range with specified shunt resistor
          print(e)

        # reset
        ina.reset()

        # low power mode
        ina.sleep()
        ina.wake()
        ```

  Docs for Adafruit ina219 library:
    - https://docs.circuitpython.org/projects/ina219/en/latest/api.html
    - In a Nutshell
      ```
      # imports
      from adafruit_ina219 import INA219
      # classes containing constants to work with INA219 methods
      from adafruit_ina219 import ADCResolution, BusVoltageRange Mode

      # initialization
      i2c_bus = board.I2C()
      ina219 = INA219(i2c_bus)
      # or specify a different bus address
      ina219 = INA219(i2c_bus, addr=INA_BUS_ADDR)
      # creating an instance of INA219 resets the device

      # the device config values are modelled as properties
      print("Config register:")
      print("  bus_voltage_range:    0x%1X" % ina219.bus_voltage_range)
      print("  gain:                 0x%1X" % ina219.gain)
      print("  bus_adc_resolution:   0x%1X" % ina219.bus_adc_resolution)
      print("  shunt_adc_resolution: 0x%1X" % ina219.shunt_adc_resolution)
      print("  mode:                 0x%1X" % ina219.mode)

      # Configure ina219 devce using set methods (use only one of them)
      ina219.set_calibration_16V_400mA()
      ina219.set_calibration_16V_5A()
      ina219.set_calibration_32V_1A()
      ina219.set_calibration_32V_2A()

      # get data
      bus_voltage   = ina219.bus_voltage   # voltage on V- (load side)
      shunt_voltage = ina219.shunt_voltage # voltage between V+ and V- across the shunt
      current       = ina219.current       # current in mA
      power         = ina219.power         # power in watts

      # Overflow detection
      if ina219.overflow:
        print("Internal Math Overflow Detected!")
      ```

## Code

  - `ra_strommessung1.py`
    From https://www.rahner-edu.de/raspberry-pi/strom-messen-mit-ina219/
    Leverages the `pi-ina219` library.

  - `ina219_simpletest.py`
    Uses the Adafruit CircuitPython ina219 library and prints out the basic
    ina219 values.

  - `battery_measure.py`
    Simple battery discharger measuring accumulated current and power.
    Stops after discharging below minimum discharge voltage. It requires a
    relais HW module in addition as depicted in the pseudo-graphic below.
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
