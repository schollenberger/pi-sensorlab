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

  Very good introduction page:
    https://www.sbprojects.net/knowledge/ir/index.php
    See navigation for the different protocols

  IR transmission is pulsed with a carrier frequency of e.g. 38kHz
  (26.3µs period) for the NEC protocol but 40kHz for the Soni SIRC protocol.
  The IR receiver filters on this frequency in order to distinguish transmission
  from background light and noise. Therefore different IR protocols may require
  different receivers.

  The IR receiver output used in this lab (something like TSOP22) is filtering
  on 38 kHz and the output is active low.  
  Datasheet: https://www.vishay.com/docs/82459/tsop48.pdf

  The IR protocols describe the representation of a logical '0' and a logical
  '1' by pulse space patterns, the start a message and the message format and
  length.
  IR protocols are all about transmitting and receiving messages. Each message
  has a start delimiter represented by a unique pulse/space pattern.

  Protocols like the NEC protocol use pulse burst of a constant duration
  (except for the start delimiter).
  The duration of the burst may vary between the protocols.
  The duration of the space following the pulse distinguish between a logical '0'
  and a logical '1' (pulse-place modulation).

  In contrast to that is the Soni SIRC protocol which uses pulse width
  modulation.

### NEC Infrared Transmission Protocol:
  References:
    https://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol
    https://exploreembedded.com/wiki/NEC_IR_Remote_Control_Interface_with_8051

  The NEC protocol's normal pulse bursts have a duration of 562.5µs
  (aprox. 21.5 periods of the carrier signal).
  Logical bits are transmitted as follows:
   - a logical '0' is defined by a 562.5µs pulse burst followed by a 562.5µs
     space, with a total transmit time of 1.125ms
   - a logical '1' is defined by a 562.5µs pulse burst followed by a 1.6875ms
     space, with a total transmit time of 2.25ms

  A message is defined as:
   - a 9ms leading pulse burst (16 times the pulse burst length used for a
     logical data bit)
   - a 4.5ms space (half time the leading pulse burst)
   - 32 data bits in the following sequence:
      - 8-bit address of the receiving device
      - 8-bit inverted of the previous value
      - 8 bit command
      - 8-bit inverted of the previous value
   - a final 562,5µs pulse burst to signify the end of message transmission.

 The NEC protocoll defines a repeat code to tell that the key is still pressed:
   - a 9ms leading pulse burst
   - a 2.25ms space
   - a 562.5µs pulse burst to mark the end of the space (and hence end of the
     transmitted repeat code).

### Sony SIRC Protocol
  see: https://www.sbprojects.net/knowledge/ir/sirc.php

  According to the link above it is using a carrier frequency of 40kHz and pulse
  width modulation with 600µs spaces in between.
  A logical '1' uses a 1.2ms pulse while a logical '0' is represented by a 600µs
  pulse.
  A 2.4ms pulse and a 600µs space signals the beginning of a message.

### Panasonic's remote protocol

  From: http://users.telenet.be/davshomepage/panacode.htm
    - Similar to the RECS-80 protocol but uses more bits.
    - doesn't really match what I am seeing.

  From LIRC code for Panasonic remote controls you find:
  https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/panasonic/DVD.lircd.conf

    ```
    name  DVD
    bits           17
    flags SPACE_ENC
    eps            20
    aeps          200

    header       4000  1600
    one           400  1200
    zero          400   400
    ptrail        400
    pre_data_bits   31
    pre_data       0x20020680
    gap          76000
    min_repeat      4
    toggle_bit      0

    frequency    36000
    ```
  That means the protocol encodes the bits via the space duration, the standard
  pulse width is 400µs, a space of 400µs represents a logical zero and a space
  of 1200µs represents a logical one.
  Header is a 4ms pulse and 1.6ms space.

  The message is 48 bit long, with a 31bit header with value `0x20020680` and
  17 command bits for which the command table is presented in the list.

  Another link shows some TV Codes that matched my remote control:
    https://tasmota.github.io/docs/Codes-for-IR-Remotes/


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
