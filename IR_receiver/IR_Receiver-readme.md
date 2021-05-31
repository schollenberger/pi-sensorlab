# IR Receiver / Sender project

  Using the IR Receiver sensor 38 kHz, B22, enables the Raspberry Pi to receive
  and interpret standard IR remote control signals.
  This allows the remote control to control the Raspi.
  Connecting an IR LED to a Raspi GPIO port enables it to send IR signals as
  well, but the Software has to take care of generating the 38 kHz pulses.
  See the section `Technical Background` for some basic understanding on IR
  technology.

  With the IR receiver connected to a GPIO pin, you can decode the IR signals
  by monitoring the GPIO port over time. There is a YouTube tutorial and some
  sample code which does it that way (low level decoding):
    https://www.youtube.com/watch?v=KhiqINyHx08
    https://github.com/Lime-Parallelogram/IR-Code-Referencer
  This project contains some python code working on this level based on the
  example from above.

  There is a package `LIRC` (Linux Infrared Remote Control) that allows
  you to decode and send infra-red signals of many (but not all) commonly used
  remote controls.
    official Web site: https://www.lirc.org
    SourceForge: https://sourceforge.net/projects/lirc/
    Remote control database for LIRC as well as WinLIRC:
      http://lirc.sourceforge.net/remotes/

  Infrared support has been added to the Linux kernel 4.18 and later.  For
  remote controls that are supported by the kernel, IR events appear just like
  keyboard or mouse events. In this case, the way to configure keymaps is
  using `ir-keytable` which comes with the package `v4l-utils`.
  See https://github.com/tompreston/python-lirc/issues/28#issuecomment-712454662
  Although this makes the LIRC daemon and LIRC clients mostly redundant in some
  use cases, LIRC offers more flexibility and functionality and is still the
  right tool in a lot of scenarios.
  See: http://lirc.sourceforge.net/lirc.org/html/configuration-guide.html#why-use-lirc
  Using LIRC on Raspberry Pie is quite popular these days.
  (from https://www.lirc.org/#top).

  This project explores as well how to interact with LIRC from a Python program.

  This project is inspired by some tutorials:
    https://tutorials-raspberrypi.de/raspberry-pi-ir-remote-control/
    https://tutorials-raspberrypi.de/raspberry-pi-fernbedienung-infrarot-steuerung-lirc/

  One of the key challenges is to analyze the IR protocol and scan codes used
  by a specific remote control device. LIRC can handle multiple remotes at the
  same time. Key names are standardized across controls as far as possible to
  help applications to support several RC devices.
  LIRC has a remote control database (see above) where people added their
  devices. Another link shows some TV Codes that matched my remote control:
    https://tasmota.github.io/docs/Codes-for-IR-Remotes/


## Technical Background

  Very good introduction page:
    https://www.sbprojects.net/knowledge/ir/index.php
    See navigation for the different protocols

  IR transmission is pulsed with a carrier frequency of e.g. 38kHz
  (26.3µs period) for the NEC protocol but 40kHz for the Sony SIRC protocol.
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

  In contrast to that is the Sony SIRC protocol which uses pulse width
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

  The timing described above matched a real Panasonic DVD remote control which
  I was using pretty well and this config did actually decode some keys.
  Comparing the scan codes with what has been seen on the raw signal
  analysis brought up some confusion. On the raw signal analysis we saw 49 bits
  instead of 48 and value of pre_data settings was found to be shifted one bit
  to the right. However, ignoring the last bit the pre_data value matched but
  the key encoding was different. This probably has something to do with the
  odd values of `bits` and `pre_data_bits`. The lirc.conf file that exactly
  matched the remote control (Panasonic_N2QAYB000124) has different settings and
  the scan codes match much better what is seen by the low level signal analysis.


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

  These instructions work for Raspian OS starting from `Stretch`, including
  `Buster` and later version.

  Note, since the Linux kernel supports infrared devices natively, a lot of
  the install instructions, e.g.:
    https://tutorials-raspberrypi.de/raspberry-pi-fernbedienung-infrarot-steuerung-lirc/
  are outdated.
  See: https://shallowsky.com/blog/hardware/raspberry-pi-ir-remote-stretch.html

  The following install instructions are pretty good (Jessie and older OS
  versions):
    https://shallowsky.com/blog/hardware/raspberry-pi-ir-remote.html
  For Strech and newer ones, follow:
    https://shallowsky.com/blog/hardware/raspberry-pi-ir-remote-stretch.html

  The LIRC package supports to decoding and sending IR signals of many
  remote controls. Since version 0.9 LIRC works together with the two kernel
  modules `gpio-ir` and `gpio-ir-tx` that are part of the Linux distribution.
  This modules have to be loaded before LIRC can be used. The kernel modules
  are controlled by the file `/boot/config.txt`. See below for details.

  In essence, LIRC consists of the service `lircd` which does the translation
  of mark and space durations to data values and matches them to a known
  remote control definition.

  Because sending and receiving infrared signals is handled by two kernel
  modules and therefore accessed via 2 different devices (`/dev/lirc0` and
  `/dev/lirc1`), you would need two instances of lircd running concurrently in
  order to send and receive IR signals without reconfiguring the lircd service.
  See https://github.com/dotnet/iot/issues/1231 for a in depth discussion of
  this topic.

  Installation steps (Raspian Buster):
    - Install the code:
      ```
      $ sudo apt-get install -y lirc
      ```
      I got version 0.10.1-6.3~deb10u1 installed (`dpkg -s lirc`).

    - Add IR kernel modules to the boot config.
      Edit file `/boot/config.txt` as root user.
      You may search for the following lines uncomment them and update
      the gpio pins. Example:
        ```
        dtoverlay=gpio-ir,gpio_pin=17
        dtoverlay=gpio-ir-tx,gpio_pin=18
        ```
      Note that if you enable both modules, and both come up successfully,
      two devices will be generated:
        - /dev/lirc0 (sender)
        - /dev/lirc1 (receiver)
      It makes sense to activate both modules as it requires a OS reboot to
      change them, but it only requires a service restart to update the lircd
      config.

    - Backup the lirc config file:
        ```
        $ sudo mv /etc/lirc/lirc_options.conf /etc/lirc/lirc_options.conf.dist
        $ sudo cp /etc/lirc/lirc_options.conf.dist /etc/lirc/lirc_options.conf
        ```
    - Update the lirc config file
        `sudo nano /etc/lirc/lirc_options.conf`
      - Be sure to set the driver to default.
        (I had it set to `devinput` which cause the command `irw` no not return
        anything.)
      - Configure lirc as an IR Receiver via the following setting:
          ```
          #device          = auto        # default
          #device          = /dev/lirc0  # sender
          device          = /dev/lirc1  # receiver
          ```
    - Disable the default remote control config file
      We disable it because it is causing warinings in the system logs.
      ```
      $ sudo mv /etc/lirc/lircd.conf.d/devinput.lircd.conf /etc/lirc/lircd.conf.d/devinput.lircd.conf.dist
      ```
    - reboot

    - Login again and check that two lirc devices exist:
      ```
      $ ls -al /dev/lirc*
      ```
      You should find two devices like this (lirc0 for output and lirc1 for
      input):
        ```
        crw-rw---- 1 root video 251, 0 May 14 00:14 /dev/lirc0
        crw-rw---- 1 root video 251, 1 May 14 00:14 /dev/lirc1
        ```

    - Verify that the lirc services started up properly
      - Check the the boot log:
        - Background on boot logs:
            On Raspian images that contain a desktop the file boot.log
            is present. However, it is not for the lite OS versions.
            Both images run systemd as the init process and the bootlogd is
            masked (set permantently inactive).
            Not clear why the boot.log file isn't created on Raspian Lite.
        - Option 1 - If the file `/var/log/boot.log` exists:
            ```
            $ sudo grep -B 3 -A 5 -i "fail" /var/log/boot.log
            ```
            Be sure you don't see old failure messages.
        - Option 2 - If no file `/var/log/boot.log` exists:
            ```
            $ journalctl -b | grep lirc  # shows the last boot
            ```
            You may list old boots using `journalctl --list-boots`. You can
            specify the boot with the parameter `-b <hash>`.
            Check file `/var/log/messagas`. Example:
            ```
            $ grep lirc /var/log/messages
            ```
        Verify that you can find the message:
          `...raspi lircd-0.10.1[602]: Notice: lircd(default) ready, using /var/run/lirc/lircd`
      - Check kernel messages
            ```
            $ dmesg | grep lirc
            ```
          Example output:
            ```
            [    7.764200] rc rc0: lirc_dev: driver gpio-ir-tx registered at minor = 0, no receiver, raw IR transmitter
            [    7.834789] rc rc1: lirc_dev: driver gpio_ir_recv registered at minor = 1, raw IR receiver, no transmitter
            ```
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

## Configure remotes and test that LIRC is working as expected

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

    - Copy some known good remote control config files into the conf directory:
      LIRC uses remove control config files that reside in the directory
      `/etc/lirc/lircd.conf.d/` and for which the file names end
      with  `...lirc.conf`.
      In this project we store all relevant remote config files on the
      Pi in the directory `$HOME/IR-Remotes`. From there the ones which need
      to be recognized by LIRC are copied to the LIRC config directory.

      - On the Pi:
        - Create the directory
            ```
            $ mkdir $HOME/IR-Remotes
            ```

      - On the host (Windows):
        - Open a bash shell
        - Change directory to `...\Raspberry-Pi-Work\IR-Remotes`
        - Execute: `scp *.* pi@raspi.wlan.local:IR-Remotes/.`

      - Back on the Pi
        - Change to the IR-Remotes directory
        - Copy over the configs of the remotes you want to test with
          e.g.:
            ```
            sudo cp N2QAYB000124.lircd.conf /etc/lirc/lircd.conf.d/.
            sudo cp VEQ0615.lircd.conf /etc/lirc/lircd.conf.d/.
            sudo cp RC-63CD.lircd.conf /etc/lirc/lircd.conf.d/.
            ```
        - Restart the lircd service:
            `sudo service lircd restart`
        - Check the file `/var/log/messages` for messages of lirc restarting.
          Browse for error messages and check for the message
          ` Notice: lircd(default) ready, using /var/run/lirc/lircd`

    - Check that the lircd service knows one of the configured remote
      controls using the command `irsend LIST`.
      Example:
        ```
        $ irsend LIST Panasonic_N2QAYB000124-TV ""

        000040040100bcbd KEY_POWER
        000040040100a0a1 KEY_INPUTAV
        0000400401000405 KEY_VOLUMEUP
        0000400401008485 KEY_VOLUMEDOWN
        0000400401002c2d KEY_CHANNELUP
        000040040100acad KEY_CHANNELDOWN
        ```
      Note: You need to get the remote name from the name parameter in the
            config file.

    - With the lircd service configured as an IR receiver, execute `irw` to
      check the remote control is correctly recognized.
      Invoke the command and press a few buttons on the remote.
      This command should display the scan code, how often the same scan code
      has been received, the associated key and the device name.
      Example:
        ```
        $ irw
        000040040100bcbd 00 KEY_POWER Panasonic_N2QAYB000124-TV
        000040040100bcbd 01 KEY_POWER Panasonic_N2QAYB000124-TV
        000040040100bcbd 02 KEY_POWER Panasonic_N2QAYB000124-TV
        0000400401002c2d 00 KEY_CHANNELUP Panasonic_N2QAYB000124-TV
        0000400401000405 00 KEY_VOLUMEUP Panasonic_N2QAYB000124-TV
        000040040100a0a1 00 KEY_INPUTAV Panasonic_N2QAYB000124-TV
        000040040100a0a1 01 KEY_INPUTAV Panasonic_N2QAYB000124-TV
        ```
      Press CTRL-C to abort the command.

    - Configure the lircd serivice as an IR transmitter:
        - Update the lircd options file:
            `sudo nano /etc/lirc/lirc_options.conf`
          Comment out the receiver device directive and enable the sender one.
          E.g:
            ```
            # device = auto      # default
            device   = /dev/lirc0  # sender
            # device  = /dev/lirc1  # receiver
            ```
        - Restart the lircd service
            sudo service lircd restart  # check the messages log

    - Test sending IR signals.
      You may check the output with a LED connected to the configured transmitter
      GPIO pin (GPIO 18).
      You need to have at least one remote control configured and no RC config
      must produce any warning when restarting the lircd service.

      Use the `irsend` command to send signals. You need to specify
      a configured remote and the key value. You may store the name of the
      remote control device in a shell variable:
        `export remote="<remote-name>"`
      Example:
        `export remote="Panasonic_N2QAYB000124-TV"`

      To find out valid keys for a specific
      remote enter:
        ```
        $ irsend LIST $remote ""
        ```
      Example, see above.

      Send a single command:
        ```
        $ irsend SEND_ONCE $remote KEY_POWER -# 10
        ```
      You should see your output LED flicker. The option `-# n` causes the
      command to be sent n times.

      Make sure you did NOT use GPIO port configured for the IR kernel via the
      GPIO library after the last boot, otherwise the LED won't work.
      So, if the LED doesn't flicker, the first thing you do is reboot and try
      again.

## Getting IR communication with LIRC to work

  Getting IR communication to work may be quite challenging.
  A lot of articles on the internet are outdated, as the LIRC / Linux Kernel
  architecture changed pretty recently.
  In the following, we assume that you are running on Raspian Buster and have
  enabled both overlays in the config.txt file as described in the
  installation part.

  Note: If you use the GPIO libraries for the same pins wile LIRC is installed
        this will remove the output port from the LIRC kernel module which means
        that neither the irsend command returns any error nor you find any error
        message in the system log files, but the LED just won't blink.
        You have to reboot in order to fix the problem.

  - Documentation links:
    - LIRC Home Page:
        https://www.lirc.org/
      It leads you to the source code Git repository, documentation, including the
      LIRC remotes database from where you can download lirc.conf files.
    - Checkout the man page:
        `$ man lirc`
    - LIRC manual:
      http://lirc.sourceforge.net/lirc.org/html/index.html

  - Double check the lirc driver config:
      `$ less /etc/lirc/lirc_options.conf`
    Be sure to set the driver to `default`.
    Be sure you have set the right driver mode (sender/receiver) by pointing
    to the correct device (lirc0/lirc1).

  - Check logs:
    - You may want to open a second command shell were show the system messages
      as a running display:
        `tail -t /var/log/messages`
      The lircd service writes info and error messages there.      
    - When you try out sending commands don't get confused by the message:
        ```
        lircd-0.10.1[513]: Info: Cannot configure the rc device for /dev/lirc0
        ```
      This message doesn't mean any problem. Running lircd at debug level shows
      that it is missing the file `/sys/class/rc/rc0/protocols`

  - Verify on Linux kernel Level
    - Check that IR input device exists.
      Read file ` /proc/bus/input/devices` Filter on `Name="gpio_ir_recv"`
      Example:
         ```
         cat /proc/bus/input/devices
         I: Bus=0019 Vendor=0001 Product=0001 Version=0100
         N: Name="gpio_ir_recv"
         P: Phys=gpio_ir_recv/input0
         S: Sysfs=/devices/platform/ir-receiver@11/rc/rc0/input0
         U: Uniq=
         H: Handlers=kbd event0
         B: PROP=20
         B: EV=100017
         B: KEY=fff 0 0 4200 108fc32e 2376051 0 0 0 7 158000 4192 4001 8e9680 0 0 10000000
         B: REL=3
         B: MSC=10
         ```
      If this device does not exist, there was a problem in loading the kernel
      module.

    - Test whether the kernel IR input module is receiving anything.
      Use the command `ir-ctl`. It allows you to check the lirc devices and
      send and receive signals in raw move (pulse duration level)

        ir-ctl --device=/dev/lirc0 -f             # shows output device features
          Example:
            ```
            $ ir-ctl --device=/dev/lirc0 -f
            Receive features /dev/lirc0:
             - Device cannot receive
            Send features /dev/lirc0:
             - Device can send raw IR
             - IR scancode encoder
             - Set carrier
             - Set duty cycle
            ```
        ir-ctl --device=/dev/lirc1 -f             # shows input device features
          Example:
            ```
            $ ir-ctl --device=/dev/lirc1 -f
            Receive features /dev/lirc1:
             - Device can receive raw IR
             - Can report decoded scancodes and protocol
             - Can set receiving timeout min:1 microseconds max:1250000 microseconds
            Send features /dev/lirc1:
             - Device cannot send
            ```

        ir-ctl --device=/dev/lirc1 -r > ir.tmp    # records some IR pattern
          Creates a file `ir.tmp` with mark and space durations.

        ir-ctl --device=/dev/lirc0 --send ir.tmp  # send some recorded IR pattern
          The LED should flicker

      If you don't see any content in the ir.tmp file or cannot see the LED flicker
      you probably have a hardware configuration mismatch.

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
    See: https://www.lirc.org/html/configure.html#lircmd.conf

## Configure actions based on remote buttons pressed:
  LIRC supports `lircrc` files to map key symbols to application-specific
  settings. There are two standard locations to place an `lircrc` file:
    ```
    $HOME/.lircrc      - user specific file`
    /etc/lirc/lircrc   - global file if no user specific file can be found
    ```
  - lircrc file format:
    See: https://www.lirc.org/html/configure.html#lircrc_format
    Example:
      ```
      # ~/.lircrc
      #
      # remote: Remote that has to launch the action
      #         e.g.: Panasonic_N2QAYB000124-DVD (optional)
      #         Default: all
      # button: button name as returned by the commands irw / irsend LIST <remote>""
      # prog:   Socket or program to receive the button string defined by
      #         the config parameter
      # config: String to pass to the program
      #
      begin
          button = KEY_UP
          prog = appleremote
          config = KEY_UP
      end
      begin
          button = KEY_DOWN
          prog = appleremote
          config = KEY_DOWN
      end
      ```
  - irexec - simple program that executes the config strings in a shell.
    Requires config file. Local one is under `.lircrc`.
    You can copy a template from `/etc/lirc/irexec.lircrc` that executes echo
    commands for the keys recognized.
    Or you can call irexec with this file (note, you have to be root to read it):
      `sudo irexec /etc/lirc/irexec.lircrc`
    You can test other lircrc files that target a different program by telling
    irexec to match for it:
      `irexec -n <prog> <lircrc config file>`

  - ircat - test lircrc config file by displaying the config string
    Example:
      `sudo ircat irexec -c /etc/lirc/irexec.lircrc`

## Using LIRC from Python programs

  Receiving IR signals is pretty easy. You just read from the LIRC socket.
  See https://github.com/akkana/scripts/blob/master/rpi/pyirw.py
  However the lirc library offers a connection object for that.

  There is a python library named `lirc` (https://pypi.org/project/lirc/) which
  supports both receiving and sending IR messages.
  The API to send messages is similar to the command `irsend`.
  The API to receive messages listens for IR button press events in the
  LIRC socket (`/var/run/lirc/lircd`) and returns strings similar to
  the command `irw`.

  The lirc library is only available for Python3. So you may want to think
  about making Python3 your system default. See document
  "Raspberry-Pi-General-memos.md" for a description on how to achieve this.

  In the following we assume Python3 is the system default. Because we ended
  up having python code in both flavors in our GIT repo, we used a Shebang line
  to make it clear.

  - Install the python lirc package (not python-lirc) to send and receive
    IR commands:
      pip install lirc

    API spec: https://lirc.readthedocs.io/en/latest/api-specification.html

  The Linux Kernel can submit IR messages as keyboard events. So in case you
  want to play with these you may find the following library interesting:
    https://pypi.org/project/keyboard/

## Other stuff

 - V4L Utility package:
     For remote control devices that are directly supported by the Linux  Kernel,
     an alternative to LIRC is to decode the IR signals using the V4l-utils
     package from the Linux TV project (https://www.linuxtv.org/) :
       https://linuxtv.org/wiki/index.php/V4l-utils

     Some doc: https://linuxtv.org/wiki/index.php/Remote_controllers-V4L

     - install ir-keytable from V4l-utils
         ```
         $ sudo apt-get install ir-keytable

         $ ir-keytable  # without options shows you the current device for IR
         $ ir-keytable -d /dev/input/event0  # verifies the input device
         $ ir-keytable -d /dev/input/event0 -r  # shows you the list of scan codes
         ```

 - Debian lirc client (not really needed for the Python lirc library)
    - Install the Debian lirc client dev libraries (not sure if still needed)
      You need to have them in order to install some python-lirc module
         sudo apt-get install  liblircclient-dev
      It should give you a lirc include directory
         ls /usr/include/lirc

 - irdb-get - comes with lirc install - use it to find remote configs and
              download them  
              irdb-get update
              irdb-get find <(partial)-keyword>

 - Running as a regular user rather than as root
   (from: https://wiki.archlinux.org/title/LIRC)
   By default, lircd runs as user root. However, for increased stability
   and security, upstream recommends running it as a regular user.
   See Appendix 14 at this link https://www.lirc.org/html/configuration-guide.html

   To do this, create and provision a lirc user:
     ```
     # groupadd -r lirc
     # useradd -r -g lirc -d /var/lib/lirc -s /usr/bin/nologin -c "LIRC daemon user" lirc
     # usermod -a -G lock,input lirc
     ```
   Augment the package-providing service unit by creating a
   lircd Systemd#Drop-in files:
    ```
    # systemctl edit lircd`


    [Service]
    User=lirc
    Group=lirc

    CapabilityBoundingSet=CAP_SETEUID
    MemoryDenyWriteExecute=true
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectHome=true
    ProtectSystem=full
    ```
    To allow /dev/lirc* devices to be accessible for the lirc group and to
    grant r/w access for the lirc group to USB devices using ACLs, copy the
    following udev rule into place:
    ```
    # cp /usr/share/lirc/contrib/60-lirc.rules /etc/udev/rules.d/
    ```
    To allow access to the lirc group to be able to create a PID file, create
    the following lircd tmpfile which will supersede the package provided one
    (which makes ownership only to root):
    ```
    /etc/tmpfiles.d/lirc.conf

    d /run/lirc 0755 lirc lirc -
    ```
    Reboot the system to verify expected function.

## Code

  Note: Linux Shebang lines (starting with `#! `) have been added to the Python
        programs and files have been made executable to tell Linux to tell which
        version of Python to use. Some scripts are written for Python 3 while
        others only work under Python 2.7.

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

 - ir-simple-decode.py (outdated)

 - pyirw.py
   Read LIRC socket in python. Copied from:
     https://github.com/akkana/scripts/blob/master/rpi/pyirw.py

 - lirc-test-receive.py
   Use the lirc python module to read IR remote control keys.
   Similar the `irw` program, it cannot detect if lircd is configured as a
   sender, so only nothing is read.

 - lirc-test-send.py
   Use the lirc python module to read IR remote control keys. It detects
   when lircd is configured for receiving and outputs a message.
