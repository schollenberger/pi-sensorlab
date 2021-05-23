# IR Receiver project

  Using the IR Receiver sensor 38 kHz, B22, enables the Raspberry Pi to receive
  and interpret standard IR remote control signals.
  This allows the remote control to control the Raspi.

  Low level tutorial:   https://www.youtube.com/watch?v=KhiqINyHx08
  Git Repo: https://github.com/Lime-Parallelogram/IR-Code-Referencer

  Decode IR Remote control signals using the tool LIRC
    LIRC - Linux Infrared Remote Control
    official Web site: https://www.lirc.org
    SourceForge: https://sourceforge.net/projects/lirc/
    Remote control database for LIRC as well as WinLIRC:
    http://lirc.sourceforge.net/remotes/

  Another link shows some TV Codes that matched my remote control:
    https://tasmota.github.io/docs/Codes-for-IR-Remotes/

  Tutorials:
    https://tutorials-raspberrypi.de/raspberry-pi-ir-remote-control/
    https://tutorials-raspberrypi.de/raspberry-pi-fernbedienung-infrarot-steuerung-lirc/

## Technical Background

  Very good introduction page:
    https://www.sbprojects.net/knowledge/ir/index.php
    See navigation for the different protocols

  IR transmission is pulsed with a carrier frequency of e.g. 38kHz
  (26.3µs period) for the NEC protocol but 40kHz for the Soni SIRC protocol.
  The IR receiver filters on this frequency in order to distinguish transmission
  from background light and noise. Therefore different IR protocols may require
  different receivers.

  The IR receiver output used in this lab (something like TSOP4838 DIP -3) is
  filtering on 38 kHz and the output is active low.  
  Datasheet: https://www.vishay.com/docs/82459/tsop48.pdf

  The IR protocols describe the representation of a logical '0' and a logical
  '1' by pulse space patterns, the start a message and the message format and
  length.
  IR protocols are all about transmitting and receiving messages. Each message
  has a start delimiter represented by a unique pulse/space pattern.

  Protocols like the NEC protocol use pulse burst of a constant duration
  (except for the start delimiter). The duration of the burst may vary between
  the protocols. The duration of the space following the pulse distinguish
  between a logical '0' and a logical '1' (pulse-place modulation).

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
    flags         SPACE_ENC
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
  This description means that the protocol encodes the bits via the space
  durations, the standard pulse width is 400µs, a space of 400µs represents a
  logical zero and a space of 1200µs represents a logical one.
  Header is a 4ms pulse and 1.6ms space.
  The message is 48 bit long, with a 31bit header with value `0x20020680` and
  17 command bits for which the command table is presented in the list.

  The timing described above matches what has been measured on a real
  Panasonic DVD remote control. Actually some keys got actually properly
  decoded using LIRC with this config but what has been seen on the raw signal
  analysis didn't quite match. We saw 49 bits instead of 48 and pre_data value
  was shifted one bit to the right. However, if we ignored the last bit the
  pre_data value matched but the key encoding was different.
  -> to be investigated still


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
    GPIO 17 (11) ->   OUT  (-> LED Blue)

    LED:

    GPIO         ->   LED
    --------------------------------
    GND          ->   GND
    GPIO 18 (12) ->   OUT  Red
    GPIO 27 (13) ->   OUT  Green
  ```

## Installation of the LIRC package

  The LIRC package supports to decoding and sending  IR signals of many
  remote controls. It contains two kernel modules (gpio-ir and gpio-ir-txt)
  that have to be loaded before LIRC can be used.
  LIRC has been better integrated with the RasPiOS in the last time.
  What you do is to uncomment the kernel modules in `/boot/config.txt`
  and adapt the gpio pin parameters (see below).

  Note, the install steps in
    https://tutorials-raspberrypi.de/raspberry-pi-fernbedienung-infrarot-steuerung-lirc/
  are outdated.
  See: https://shallowsky.com/blog/hardware/raspberry-pi-ir-remote-stretch.html

  Note as well that LIRC daemon (service) can either act as an IR receiver or
  as an IR sender at the same time. You have to run two instances of the lircd
  service concurrently if you want to be able to receive and send IR signals
  at the same time.
  See https://github.com/dotnet/iot/issues/1231 for a in depth discussion of
  this topic.

  This is what I did to be successful:
    - Install the code:
      ```
      $ sudo apt-get install -y lirc
      ```
    - Note: You don't update the file `/etc/modules` anymore!
      Note: the file `/etc/lirc/hardware.conf` is outdated as well!
    - Add lirc kernal modules to the boot config.
      Edit file `/boot/config.txt` as root user.
      You may search for the following lines uncomment them and update
      the gpio pins.
      ```
      dtoverlay=gpio-ir,gpio_pin=17
      dtoverlay=gpio-ir-tx,gpio_pin=18
      ```
      Note that if you enable both modules, and both come up successfully,
      two devices will be generated:
        - /dev/lirc0 (sender)
        - /dev/lirc1 (receiver)
    - Update the file `/etc/lirc/lirc_options.conf`
      e.g. `sudo nano /etc/lirc/lirc_options.conf`
      Be sure to set the driver to default.
      (I had it set to `devinput` which cause the command `irw` no not return
      anything.)
    - Configure lirc as an IR Receiver via the following setting:
        ```
        # device auto      # default
        # device /dev/lirc0  # sender
        device /dev/lirc1  # receiver
        ```
    - reboot
    - Login again and check that two lirc devices exist:
      ```
      $ ls -al /dev/lirc*
      ```
      You should find two devices like this (lirc0 for output and lirc1 for input):
        ```
        crw-rw---- 1 root video 251, 0 May 14 00:14 /dev/lirc0
        crw-rw---- 1 root video 251, 1 May 14 00:14 /dev/lirc1
        ```
    - Check the the boot log:
      - Option 1: if you the file `/var/log/boot.log`exists
        (not the case on on Raspian Buster Lite)
          ```
          $ sudo grep -B 3 -A 5 -i "fail" /var/log/boot.log
          ```
          Be sure you don't see old failure messages.
      - Option 2:
          ```
          $ journalctl -b | grep lirc  # shows the last boot
          ```
          You may list old boots using `journalctl --list-boots`. You can
          specify the boot with the parameter `-b <hash>`.
        or
          ```
          $ dmesg | grep lirc
          ```
      - Background: On Raspian images that contain a desktop the file boot.log
                    is present. However not for the lite OS versions.
                    Both images run systemd as the init process and the bootlogd
                    is masked. Not clear why the boot.log file isn't created on
                    Raspian Lite.
      - Note:  In LIRC version 0.10.1 the default remote control config file
               causes a few error messages containing
               `Multiple values for same code:` We will fix this later by
               disabling the standard RC config file.
               `/etc/lirc/lircd.conf.d/devinput.lircd.conf`

    - Check the modules load service status:
      ```
      $ systemctl status systemd-modules-load.service
      ```
    - Check the services:
      ```
      $ service lircd status   # basic device driver
      $ service lircmd status  # LIRC mouse daemon
      ```
      The `lircmd` daemon Converts IR remotes button presses to mouse movements
      and clicks.
      Example output for the lircmd service:
      ```
      lircmd.service - Convert IR remotes button presses to mouse movements and clicks
        Loaded: loaded (/lib/systemd/system/lircmd.service; disabled; vendor preset: enabled)
        Active: inactive (dead)
          Docs: man:lircmd(8)
                http://lirc.org/html/configure.html
      ```
    - Check that LIRC is receiving signals from a remote control.
      Execute: `sudo mode2 --driver default -d /dev/lirc1`
      Press a key on your remote control and you should see
      a sequence of `pulse ...`, `space ...` lines.
      Example:
        ```
        $ mode2 -d /dev/lirc1
        Using driver default on device /dev/lirc1
        Trying device: /dev/lirc1
        Using device: /dev/lirc1
        space 16387666
        space 16360028
        pulse 3471
        space 1733
        pulse 488
        ...
        space 1332
        pulse 448
        pulse 140394  # <-- timeout
        ```
    - Disable the default remote control config file and add some good ones.
      Note: The file names for the remotes are subject to change.
      The lirc service maps IR codes to buttons pressed on the RC (remote
      control) so that software may work independently from the type of RC used.
      This is achieved via a configuration with a name like `...lirc.conf`
      placed in the directory `/etc/lirc/lircd.conf.d/`
      A large number of these config files can be downloaded (see link section).
      In the following we copy a few files that proved to work in order to be
      able to continue verifying the system:
      - On the Pi create a directory `$HOME/IR-Remotes`
      - On the host (Windows) open a bash shell and cd into the directory
        `...\Raspberry-Pi-Work\IR-Remotes`
      - Execute:
          scp *.* pi@raspi.wlan.local:IR-Remotes/.
      - Back on the Pi cd into the IR-Remotes directory and copy over a few
        configs - e.g.:
          sudo cp DVD.lircd.conf /etc/lirc/lircd.conf.d/.
          sudo cp RC-63CD.lircd.conf /etc/lirc/lircd.conf.d/.
      - Deactivate the standard config file:
          sudo mv /etc/lirc/lircd.conf.d/devinput.lircd.conf /etc/lirc/lircd.conf.d/devinput.lircd.conf.dist
      - Restart the lircd service:
          sudo service lircd restart
      - Check the fail `/var/log/messages` for messages of lirc restarting.

    - Check that the lircd service knows the DVD remote control:
        irsend LIST DVD ""
      You should see a few codes and button names listed.

    - With the lircd service configured as an IR receiver,
      execute `irw` to check the the remote control is correctly recognized.
      This command displays the scan code, the key and the device name that matched
      the key.
      Example:
        ```
        $ irw
        000040040d00000d 00 KEY_STOP DVD
        000040040d00606d 00 KEY_PAUSE DVD
        000040040d00505d 00 KEY_PLAY DVD
        ```
      Press CTRL-C to abort the command.
    - Configure the lircd serivice as an IR transmitter:
        - Update the lircd options file:
            `sudo nano /etc/lirc/lirc_options.conf`
          Comment out the receiver device directive and enable the sender one.
          E.g:
            ```
            # device auto      # default
            device /dev/lirc0  # sender
            # device /dev/lirc1  # receiver
            ```
        - Restart the lircd service
            sudo service lircd restart  # check the messages log
    - Test sending IR signals.
      You may check the output with a LED connected to the configured transmitter
      GPIO pin (GPIO 18).
      You need to have at least one remote control configured and no RC config
      must produce any warning when restarting the lircd sercive.

      You may use the `irsend`command to send signals. You need to specify
      a configured remote and the key value. To find out valid keys for a specific
      remote enter:
        ```
        $ irsend LIST <remote-name> ""
        ```
      e.g.:
        ```
        $ irsend LIST DVD ""

        000000000000606d KEY_PAUSE
        000000000000505d KEY_PLAY
        000000000000000d KEY_STOP
        0000000000008984 KEY_SUBTITLE
        000000000000ccc1 KEY_AUDIO
        ...
        ```
      Send a single command:
        ```
        $ irsend SEND_ONCE DVD KEY_PLAY
        ```
      You should see your output LED flicker.

      Make sure you did use the same GPIO port via the GPIO library after
      the last boot, otherwise the LED won't work.
      If it doesn't work the first thing you do is reboot and try the
      command again.

## Getting LIRC to work

  Note that a lot of articles on the internet are outdated, as the LIRC
  architecture changed pretty recently.
  In the following, we assume that you have enabled both overlays in the
  config.txt file as described in the installation part.

  Note: If you use the GPIO libraries for the same pins wile LIRC is installed
        this will remove the output port from the LIRC kernel module which means
        that neither the irsend command returns any error nor you find any error
        message in the system log files, but the LED just won't blink.
        You have to reboot in order to fix the problem.

  - Checkout the lirc home page:
      https://www.lirc.org/
    It leads you to the source code Git repository, documentation, including the
    LIRC remotes database from where you can download lirc.conf files.
  - Checkout the man page:
      `$ man lirc`
  - Check the lirc driver config:
      `$ less /etc/lirc/lirc_options.conf`
    Be sure to set the driver to `default`.
    Be sure you have set the right driver mode (sender/receiver) by pointing
    to the correct device (lirc0/lirc1).

  - You may want to open a second command shell were show the system messages
    as a running display:
      `tail -t /var/log/messages`
    LIRC writes info and error messages there.
    Note: When you try out sending commands don't get confused by the message:
      ```
      lircd-0.10.1[513]: Info: Cannot configure the rc device for /dev/lirc0
      ```
    This message doesn't mean any problem. Running lircd at debug level shows
    that it is missing the file `/sys/class/rc/rc0/protocols`

  - Test that the lirc device is receiving anything using the command:
      `sudo mode2 --driver default -d /dev/lirc1`
    as described in the previous section.
    (We use use the parameters `--driver` and `-d` to overwrite the lirc config
    settings.)
    This should work even if the lircd service is bound to the sender device.
    If you don't see any signals you probably have a hardware configuration
    problem.

  - Run the lircd service locally with different options / trace level:
      ```
      $ sudo service lircd stop
      # or use
      $ sudo pkill -SIGTERM

      $ ps -ef | grep lircd   # should show no running process except
                              # the grep command
      $ sudo lircd --nodaemon -D10 --device /dev/lircX -i
                              # enter lircd -h for a list of valid options

      # execute the tests in a different shell window

      $ CTRL-C  # stops the service

      $ sudo service lircd start

      ```

## Configure remote control devices:
    LIRC supports several remotes in parallel. For each remote it requires
    a lirc.conf file similar to the one depicted in the technical background
    section.
    You have two options:
      - Download one from the remotes database
        (http://lirc.sourceforge.net/remotes/)
      - Use the program `irrecord` to capture the key message codes from an
        existing device.
    In any case you have to copy the lircd.conf files to the directory:
      `/etc/lirc/lircd.conf.d/`.
    Note after you updated the config directory you have to restart the lircd
    service (`sudo service lircd restart`).
    - Use files from the remotes database:
      If not done yet, copy the standard conf files from the Windows PC
        `Windows bash$ scp -r IR-Remote pi@raspi.wlan.local:.`
      You may clone the GIT repo as well:
        $ cd $HOME/workspace/git.code.sf.net
        $ git clone git@lirc-remotes-code...
    - Read the IR codes from an existing remote control.
      Use the command `irrecord`. Note by default this tool requires you to use
      pre-defined key codes. You can print them out via the following command:
        ```
        irrecord --list-namespace > lirc-namespace.txt
        ```
      Now you can capture the codes via the command:
         ```
         irrecord [-d /dev/lirc0]
         ```
      You get prompted to specify the device name and the config file.
      Note there is an option to update an existing config file as well
      (see help page).
      When you are finished, copy that file over to `/etc/lirc/lircd.conf.d/`,
      and restart the service `lircd`.
      You may check the file `/var/log/messages` to check which remotes are
      configured and whether these files contain errors.

## More stuff to configure on LIRC
  - Configure mouse driver `lircmd`
    See: https://www.lirc.org/html/configure.html
  - Use LIRC to execute commands: `irexec`:
    Requires config file. Local one is under `.lircrc`.
    You can copy a template from `/etc/lirc/irexec.lircrc` that executes echo
    commands for the keys recognized.


    ## worked once now install is broken

## Code

  - ir-read-binary.py (outdated)
    Derived from low level tutorial:
    https://github.com/Lime-Parallelogram/IR-Code-Referencer

    Raw read via GPIO module.
    Assumes a go-zero protocol, with longer start pulse.
    Outputs result in hex (no trimming).
    Extended logging in the code revealed the burst and space durations on
    a Panasonic DVD / TV remote control.
    Code has been modified to properly decode the Panasonic remote control
    messages.
    However it showed that every remote is different. So device specific
    versions to analyze the raw IR signals have been created:
     - ir-analyze-panadvd.py
     - ir-analyze-VEQ0615.py
    See below.

 - ir-analyse-panadvd.py / ir-analyse-VEQ0615.py
   Derived from low level tutorial:
   https://github.com/Lime-Parallelogram/IR-Code-Referencer

   Analyze the signals from a IR detector connected to a GPIO port. It mirrors
   what has been read on another GPIO port (e.g. connected to a LED for optical
   reference).
   Output LED has been set to a different port than used by LIRC to avoid
   conflicts.
   The code contains a few flags and config values to decode the IR messages.
