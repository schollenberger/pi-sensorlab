# RGB Project
  Code to drive an RGB LED from Raspberry Pi.

  First project using the Raspi GPIO.
  GPIO pinout: https://pinout.xyz

  Local command: `pinout`

  The bash script in thos project is using the Wiring-Pi library
  (which is deprecated in the meantime).
  It has a CLI executable (https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility).

  Phython scripts are using the RPi.GPIO library from https://pypi.org/project/RPi.GPIO/

  You may want to check out the libary `gpizero` which comes with the Raspi OS
  (https://gpiozero.readthedocs.io/en/stable/).

  An alternative is the `Adafruit CircuitPython` GPIO libraries.

## HW Setup

Connect the `Allnet RGB LED B09` to the Pi GPIO port:
```
  Sensor Pins:

     +----------------+
   --+ R+ (Red)       |
     |                |
   --+ G+ (Green)     |
     |         (LED)  |
   --+ B+ (Blue)      |
     |                |
   --+ GND            |
     +----------------+

  GPIO         ->   B09 Sensor
  --------------------------------    
  GND          ->   GND
  GPIO 17 (11) ->   Blue
  GPIO 27 (13) ->   Green
  GPIO 22 (15) ->   Red
```

## Bash Code

 - `toggle-led.sh`
   Go in 4 cycles through the colors
   Uses the gpio command.

 - `toggle-led.py`
   Python implementation using the native RPi.GPIO python module

 - `light-barrier.py`
   Python script that switches the RGB LED module from green to red based on
   the light barrier sensor (`Allnet Light Barrier B18`) being tripped or not.
   Again based on the RPi.GPIO module

 - `gpio_pwn_test.py` and `gpio_pwn_rgb.py`
   Small test programs to play with the
