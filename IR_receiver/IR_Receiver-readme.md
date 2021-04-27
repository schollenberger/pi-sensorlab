# IR Receier project

  Using the IR Receiver sensor 38 kHz, B22, enables the Raspberry Pi to receive
  and interpret standard IR remote control signals.
  This allows the remote control to control the Raspi.

  Low level tutorial:   https://www.youtube.com/watch?v=KhiqINyHx08
  Git Repo: https://github.com/Lime-Parallelogram/IR-Code-Referencer

  Decode IR Remote control signals using the tool LIRC
    LIRC - Linux Infrared Remote Control
    official Web site: https://www.lirc.org
    SourceForge: https://sourceforge.net/projects/lirc/
    Remote control database for LIRC as well asWinLIRC: http://lirc.sourceforge.net/remotes/

## Technical Background

  The protocol of IR remote controls ... #tbd#

  The IR receiver output is active low.

## HW Setup

  Connect the `IR receiver 38 kHz B22` to the Pi GPIO port:
  ```
    Sensor Pins:

       +----------------+
     --+ +5V            |
       |                |
     --+ GND            |
       |                |
     --+ OUT            |
       +----------------+

    GPIO         ->   B22 Sensor
    --------------------------------    
    GND          ->   GND
    3.3V         ->   +5V
    GPIO 24 (18) ->   OUT
  ```

## Installation

  ## installation of LIRC


## Code

  - ir-read-binary.py
    Derived from low level tutorial: https://github.com/Lime-Parallelogram/IR-Code-Referencer

    Raw read via GPIO module.
    Assumes a go-zero protocol, with longer start pulse.
    Outputs result in hex (no trimming)
