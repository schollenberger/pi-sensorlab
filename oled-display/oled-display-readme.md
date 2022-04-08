# AZ-Delivery OLED Display Project

  This project is about working with OLED displays that are connected via the
  I2C bus to a Raspberry Pi. We cover two displays with two different controller
  chips. One of them is the AZ-Delivery OLED Display 1.3 inch which uses
  the SH1106 chip and the other one, the 0.93 inch display, is based on the
  SSD1306 chip.

  Both displays use the I2C bus, similar to the INA219 board which has already
  be used to measure current and voltage (see separate ina219 project).

  The OLED Displays from AZ-Delivery are configured to port 0x3c. Therefore they
  can run aside the INA219 board which uses a port in the range of 0x4x.

  This project covers the HW set up, some sample code to drive these
  displays, and Python classes which represent the display device  in order
  to ease interchanging OLED and LCD displays.

  The code in this project runs on Python3 interpreter only. So this version
  has to be configured as the system default for the instructions in his readme
  to work (check with `pip -V` and `python -V`, both capital V).

  We have investigated on two the python libraries to drive the displays:
  `luma.oled` (https://pypi.org/project/luma.oled/) supports both controllers,
  SH1106 and SSD1306 while the library from Adafruit CircuitPython for OLED
  displays, only supports the SSD1306 controller. There is an Adafruit SH1106
  display driver available, but we didn't get it to work.
  While the SSD1306 controller is pretty much compatible with the SH1106 chip
  and works pretty will with a SH1106 device driver, running a SH1106 display
  with a SSD1306 driver doesn't work at all.

  The Adafruit libraries are supported well and have been used for the
  LCD displays and the INA219 board. But Adafruit doesn't sell OLED displays
  using the SH1106 controller so this failure isn't a surprise. We found a
  SH1106 driver and examples of displays connected via SPI, but we couldn't
  get it to work with the I2C bus.

  For installing Python interpreters and making V3 default, see the
  Raspberry-Pi-Install readme.

  See the usage section for more details on how to program a pixel based
  display like the OLED ones as you need more than just the device driver
  libraries.


## Link to the Tutorial I followed:
  https://www.raspberry-buy.de/I2C_OLED-Display_Raspberry_Pi_Python_SH1106_SSD1306.html

  In addition the eBook from AZ-Delivery which has been downloaded from their
  Web Shop has been used.

## Hardware setup
### 1.3" I2C OLED Display
  It uses the SH1106 chip and has a resolution of 128x64 pixel.

  ```
    +----------------------------+
    |        o   o   o   o       |
    |        1   2   3   4       |
    |       VCC GND SCL SDA      |
    |                            |
    |  +-----------------------+ |
    |  |                       | |
    |  |                       | |
    |  |                       | |
    |  |                       | |
    |  |                       | |
    |  +-----------------------+ |
    +----------------------------+

  ```
  Connect the OLED Display the following:

  ```
    RaspberryPi     ->  OLED Display
    ---------------------------------
    Pin 1 (3.3V)    ->  VCC (1)
    Pin 3 (GPIO 02) ->  Sda
    Pin 5 (GPIO 03) ->  Scl
    Pin 6 (GND)     ->  GND (2)

  ```
### HW 1.3" I2C OLED Display
  It uses the SSd1306 chip and has a resolution of 128x64 pixel.
  !!! Pinout is similar but VCC and GND are swapped !!!

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
  Connections between the OLED Display are the same as for the 1.3 inch display.
  Except the pin swap between VCC and GND.


## Install
  Most of the stuff below might already be installed on a full Raspi OS.
  We pre-req that Python3 is already installed properly and configured to be
  the default. See `Raspberry-Pi-General-memos.md` for how to configure the
  python default

### Basics
  As always start with update and upgrade, then install i2c support:
  ```
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install -y i2c-tools
  sudo apt-get install -y python3-rpi.gpio
  ```  

### PIL - Python imaging library - pillow project
  In order to display something programmatically, you need this image library:
  ```
  sudo apt-get install -y libffi-dev libssl-dev libjpeg-dev zlib1g-dev
  sudo apt-get install -y libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5
  sudo apt-get install -y python3-pil
  sudo apt-get install fonts-dejavu # some true type fonts
  ```

  If you prefer to generate it from the source use:
  ```
  pip install --upgrade Pillow
  ```

### luma.oled driver
  For SSD1306 controllers either the luma.oled library or the Adafruit library
  will work. For SH1106 you have to install the luma.oled.
  ```
  pip install luma.oled  # this installs the luma.core module as well
  ```

  Typical imports in code using luma:
  ```
  from luma.core.interface.serial import i2c
  from luma.core.render import canvas
  from luma.oled.device import sh1106, ssd1306
  from PIL import ImageFont, ImageDraw, Image
  ```

### Adafruit CircuitPython libraries
  A pre-rq is that you have to have Blinka installed whicn gives you
  CircuitPython support on the Raspberry Pi. (see install memos.)

  Git Repo:
     https://github.com/adafruit/Adafruit_CircuitPython_SSD1306

  See: https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

  The device driver should be only on python install:
  ```
    sudo pip3 install adafruit-circuitpython-ssd1306
  ```
  This library depends on the following CircuitPython modules but they should
  install under the cover:
    - Bus Device: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
    - Framebuf:   https://github.com/adafruit/Adafruit_CircuitPython_framebuf

  Typical imports in code using Adafruit
  ```
  from board import SCL, SDA
  import busio
  import adafruit_ssd1306
  from PIL import ImageFont, ImageDraw, Image
  ```

### Adafruit and SH1106
  There is sample code which uses the Adafruit CircuitPython OLED libraries in
  conjunction with the SSD1106 display, however we didn't succeed to get the
  Adafruit SH1106 driver to work over the I2C bus.

  The effort in getting Adafruit CircuitPython libraries for our I2C display
  with SH1160 controller is documented here for reference only:

  Python support for the SSH116 display controller.
      https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_SH1106
      https://pypi.org/project/adafruit-circuitpython-displayio-sh1106/
  (Examples are only available for SPI bus. So we did some guessing trying to
  get the display working.)

  Some pre-reqs had to be installed in addition:
  ?? Not sure if  NumPy, a numerical package has to be installed yet.
  ```
    # sudo apt-get install python3-numpy
    sudo pip3 install adafruit-circuitpython-rgb-display
  ```
  We saw the Adafruit packages try to install numpy via Pyhton wheels but
  that did go well. After installing numpy on the OS level the pyhton packages
  installed successfully.
  For the Adafruit libraries, we followed:
  https://learn.adafruit.com/adafruit-1-14-240x135-color-tft-breakout/python-wiring-and-setup

  Once you satisfy the Blinka pre-req, and NumPy install the OLED display
  support as follows:
  ```
    pip install adafruit-blinka-displayio
    pip install adafruit-circuitpython-display-text
    pip install adafruit-circuitpython-displayio-sh1106
  ```
  That satisfies the following imports:
  ```
    import busio              # from Blinka
    import displayio          # not sure whether this now comes from
                              # adafruit-circuitpython-rgb-display or from
                              # adafruit-blinka-displayio.
    import terminalio         # same as above
    from adafruit_display_text import label
    import adafruit_displayio_sh1106
  ```
  Some links:

  https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage
  https://www.raspberrypi-spy.co.uk/2018/04/i2c-oled-display-module-with-raspberry-pi/
  https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2

  https://www.heise.de/select/make/2017/3/1498421637812722


## Check setup

  - Check I2C bus on PI
      sudo i2cdetect -y 1

  - List already installed fonts. This is useful when you want to write with
    special fonts on the display.
       fc-list

  - Check I2C bus speed
    Edit `/boot/config.txt` and check for the dtparam=i2c_baudrate.
    If empty add an entry to set it to 1MHz to speed up the display.
    ```
    sudo nano /boot/config.txt

    dtparam=i2c_baudrate=1000000
    ```
    You see the effect drastically on the 3D box example

## Usage
  On a low level, OLED display devices take bitmaps and displays them. In order
  to programmatically show anything on the display, you need 2 things:
    - an OLED device driver:
      an abstraction of the display device (which matches the controller chip)
    - an Imaging Library:
      a library that creates a bitmap based on various draw commands (rectangle,
      text, arcs, ...).

  As outlined in the beginning, OLED device drivers are available from
  the luma project for a number of controller chips and from Adafruit where
  the SSD1306 chip is the only one which is well supported.
  Both device drivers work with PIL (Python Imaging Library) which is maintained
  by the `pillow` project.

### luma library usage
  See: https://luma-oled.readthedocs.io/en/latest/python-usage.html
       https://luma-core.readthedocs.io/en/latest/intro.html

  `luma.core` is a component library providing a Pillow-compatible drawing
  canvas for Python 3, and other functionality to support drawing primitives
  and text-rendering capabilities for small displays on the Raspberry Pi and
  other single board computers.

  The OLED library gives you a display device object which allows you to display
  bitmaps. When the program ends, the display is cleared as well.
  This may not always be what you want. Short doc summary for the
  luma.oled.device class:
  ```
  luma.oled.device

     class luma.oled.device.sh1106(serial_interface=None,
              width=128, height=64, rotate=0, **kwargs)
        Serial interface to a monochrome SH1106 OLED display.

     On creation, an initialization sequence is pumped to the display to
     properly configure it. Further control commands can then be called to
     affect the brightness and other settings.

     Methods:
        capabilities(width, height, rotate, mode='1')
           Assigns attributes such as width, height, size and bounding_box
          correctly oriented from the supplied parameters.

        clear()
           Initializes the device memory with an empty (blank) image.

        display(image)
           Takes a 1-bit PIL.Image and dumps it to the SH1106 OLED display.

        hide()
           Switches the display mode OFF, putting the device in low-power
           sleep mode.

        show()
           Sets the display mode ON, waking the device out of a prior low-power
           sleep mode.
  ```

  Note that luma is even more powerful. E.g. it contains display emulators to
  enable coding without a display device.

  The luma examples use the class luma.core.render.canvas in a transaction
  context (with clause) to draw on an OLED display. This is nice in a real
  program but it annoying when trying the commands out in a Python shell.

  Here what happens under the cover when using a canvas object:  
  The with clause creates a transaction context calling the canvas.__enter__()
  method at the beginning and canvas.__exit__(None,None,None) at the end.
  Upon creation the canvas object it internally calls
  Image.new("RGB", device.size) to create an empty PIL Image object.
  Within  canvas.__enter__() it creates a PIL ImageDraw.Draw object for that
  image and returns it.
  With the ImageDraw.Draw object you can execute draw commands on image
  unitl the __exit__ method gets called which causes the image to be displayed
  on the device using `display()` on the luma OLED device object.

  The modules Image and ImageDraw are part of the Python Image Library (PIL),
  which is a generic framework to manipulate bitmaps and bitmap files.

  There are examples in GitHub on how to program with luma. You may need to
  adapt the code by creating and handing over your specific device object:
     https://github.com/rm-hull/luma.examples
  Some of them have been copied to this repo and adapted to work with our setup.

### Adafruit library usage
  The Adafruit OLED library works a bit different than the luma.oled as it
  doesn't clear the display at the end of the program.
  But it takes the same PIL Image objects to display them on the device.

  You create the display device passing the I2C object and the display's
  dimensions:
  Example: `disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)`

  Lateron, you can query the device size via its attributes `width` and `height`
    ```
    width = disp.width
    height = disp.height  
    ```
  The device has a couple of methods:
    - fill([0|1])
      Fills the whole display buffer with either black or white pixels.

    - pixel(x, y, color)
      Sets a pixel on the display's buffer.

    - image(image)
      Loads an image to the display buffer.      

    - show()
      Actually transfer display buffer to the display.

    - invert(invert: bool)
        True: sets black on white background (inverts display)  
        False: resets to white on black background  

    - rotate(rotate: bool)
        False: Rotates by 180 degrees
        True:  Sets rotation back
        Vertical mirror is effective immediately
        For seg remap to be visible you need to call show()

     - poweroff(), poweron()
        Turns the diaplay off and on again.

  In order to display some shapes or text, you create a PIL image object with
  the correct size and a corresponding ImageDraw object. This results in a
  bitmap that you transfer on the display.

  Example:
    - for creating an image a draw object:
      ```
      image = Image.new('1', (width, height))
      # Get drawing object to draw on image.
      draw = ImageDraw.Draw(image)
      ```

    - Now you can create content on the display, but it will not yet been shown.
      Example: `draw.rectangle((0, 0, width, height), outline=1, fill=0)`

    - At the end you have to call:
      ```
      disp.image(image)
      disp.show()
      ```

### Python Imaging Library
  see: https://pillow.readthedocs.io/en/stable/index.html

  The Python Imaging Library adds image processing capabilities to your
  Python interpreter.

  The most important class is `Image`. Image instances can be loaded from
  image files or can be created from scratch.
  Example:
    ```
    from PIL import Image

    # Image from file
    im = Image.open("pic.png")
    print (im.format, im.size, im.mode)

    # Reading from open file
    with open("pic.png", "rb") as fp:
       im=Image.open(fp)

    # Image from scratch,
    mysize=(128,64) # width, height
    mymode="RGB" # Modes examples:
                 #   "1" -   1-bit px,
                 #   "L" -   8-bit px,
                 # "RGB" - 3x8-bit px true color)
    im = Image.new(mode=mymode,size=mysize,color=0x30A020) # green box
    ```

  There are a number of methods to process an Image object. When processing
  image files you store the result using method `save(file, format)`.

  There is a `show()` method as well but in order for this to work, you have
  to properly setup the Pillow Image-Plugin.

  The Image class offers a number of method to modify the image, e.g. create
  tumbnails, cut and paste regions, resize, rotate, etc.
  Sample code:
    ```
    from PIL import Image
    # Image from file
    im = Image.open("pic.png")
    im.save("pic.jpg", "JPEG") # save in JPEG format
    size = (128,128)
    im.thumbnail(size)
    im.save("pic-thumbnail.jpg", "JPEG")
    # Cut, rotate and paste a subrectangle
    box = (20,20,100,100)
    region = im.crop(box)
    region = region.transpose(Image.ROTATE_180)
    im.paste(region,box)
    im.save("pic-mod.jpg", "JPEG")
    # other methods
    im.resize(size)
    im.rotate(45) # degrees counter-clockwise
    out = im.transpose(Image.FLIP_LEFT_RIGHT)
    ```

  In order to draw or write on an Image object you need the module `ImageDraw`.
  With this module you may instantiate a `Draw` object which support drawing
  lines, rectangles, arcs, etc. and writing texts in specified fonts.
  Example:
    ```
    import sys
    from PIL import Image, ImageDraw, ImageFont

    # create an image
    out = Image.new("L", (150, 100), 128) # gray-scale

    # get a font
    fnt = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 14)

    # get a drawing context
    d = ImageDraw.Draw(out)

    # draw a white cross
    d.line((0, 0) + out.size, fill=255)
    d.line((0, out.size[1], out.size[0], 0), fill=255)

    # draw a black text
    d.text((10, 10), "Greetings !", font=fnt, fill=0)

    # draw multiline text
    d.multiline_text((10, 30), "Hello\nWorld", font=fnt, fill=0)

    # write to stdout
    out.save("out.png", "PNG")
    ```

  When writing text you need to specify a font using the PIL `ImageFont` module.
  With this module you can load bitmap fonts (.pil) and truetype fonts (.ttf).
  Note that these fonts have to be installed on your system.
  If you don't care about specific fonts you can load a default font.
  Examples:
    ```
    from PIL import ImageFont, ImageDraw

    font = ImageFont.load(arial.pil)  # bitmap font
    font = ImageFont.truetype('DejaVuSansMono-Oblique.ttf', 14) # TrueType with size
    font = ImageFont.load_default()
    ```
  For TrueType fonts you may retrieve the name and the size attributes.
  Example:
    ```
      font.getmetrics()  -> (13,4)  # baseline to highest/lowest point
      font.getname()     -> ('DejaVu Sans Mono', 'Oblique')
    ```

  In the context of OLED displays, either instantiate the ImageDraw.Draw class
  based on the luma.core.canvas object or, in case of the Adafruit libraries,
  instantiate a 1-bit Image from which you create the Draw object and later
  let the device display the image.

## Code
  - oled-adafruit-clear.py
    Simply clears the display using the Adafruit library.

 - oled-adafriot-simple.py
   Simple stuff using the Adafruid OLED lib
   If interrupted the display remains.

  - oled-adafruit-stats.py
    Print out IP, CPU load, Memory and Disk on the display.
    It uses the Adafruit OLED library.
    From: https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

  - oled-sh1106-3dbox.py
    Adapted from https://github.com/rm-hull/luma.examples

  - oled-sh1106-clock.py
    Adapted from https://github.com/rm-hull/luma.examples

  - oled-ssh1106-simple1.py
    First exercise to use the luma.oled library putting a rectangle and
    some text on the display.
    Derived from:
    https://www.raspberry-buy.de/I2C_OLED-Display_Raspberry_Pi_Python_SH1106_SSD1306.html

  - oled-sh1106-simple2.py
    Displaying other stuff based on the code structure of oled-ssh1106-simple1.py
    It shows that with the font: `DejaVuSansMono-Oblique.ttf 10pt` you can
    display 20 chars and 4 lines it still leaves you some space on both
    dimensions.

  - oled-ssd1306-3dbox.py, oled-ssd1306-3dbox.py
    Adapted from https://github.com/rm-hull/luma.examples
    Adapted by setting the controller to SSD1306

  - oled-ssd1306-simple2.py
    Simple stuff luma lib with ssd1306 device
