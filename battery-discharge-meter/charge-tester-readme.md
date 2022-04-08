# Charge Tester Readme

  Here, we document the charge/discharge characteristics of a battery charger.

## Test setup

  We leverage the HW setup of the battery discharge meter. Instead of connecting
  it to a battery/load resistor circuit we pull wires to the battery inside the
  charger.

  Complete setup (w/o display):
  ```
                                              +--------------+
                                           +--+-- CH0        |
                                           |  |              |
      +-------------------------+          |  | AD-Converter |
      |       Charger           |          |  |              |
      |                         |      +------+-- AGND       |
      |     *                   |      |   |  +--------------+
      |     *-----------------------o------+
      |     -----------+        |      |   |  +-------------+
      |    +*+         +------------o----+ |  |   ina960    |
      |    | |                  |      | | |  +-------------+
      |    | |                  |      | | +--+-- Vin+      |
      |    | |                  |      | |    |             |
      |    | |                  |      | +----+-- Vin-      |
      |    +-+                  |      |      |             |
      |     *--------------------------0------+-- GND       |
      |                         |             +-------------+
      +-------------------------+
  ```

## Install

  This project has the same pre-reqs as the Battery Discharge Meter project.
  Setup instructions may be found in the appropriate readme file.

## Code

  -


## Results

  This is how the `Conrad Charge Manager 2000` operates.
  They have been examined with the setup above by measuring the voltages of
  the charger and the battery (with the INA960 shunt in between) using an
  oscilloscope.

  ** Preliminary results **
  This charger switches between charge / discharge current and the measurement
  of the battery voltage.
  ```  
  Discharge:
    Period:           9 sec
    Drain phase:      2 sec
    Relax phase:      7 sec

    AAA battery:
      Drain current:      1200 mA
      Mean drain current:  267 mA  


  Charge:
    Period:           9 sec
    Drain phase:      2 sec
    Relax phase:      7 sec

    AAA battery:

  ```    
