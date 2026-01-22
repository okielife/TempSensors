Building Your Own
=================

This covers the assembly of one of these temperature sensors

.. important::
    There are a few tools which will be needed to construct this.

    - The primary one is the 3D printer itself.
      I am getting by with a very small hobby 3D printer that I got off of Amazon `here <https://www.amazon.com/dp/B0CMHM6XQG>`__.
      It has a very small print area, which has forced me to rethink the design multiple times, for better or for worse.
    - The other ones include some very small screw drivers, both flat and phillips, and both in the 1-3mm range.
      A set like `this <https://www.amazon.com/Screwdriver-Flathead-Phillips-Screwdrivers-Computer/dp/B0BMWQNMPS/>`__ is great.
    - You will also want some wire strippers for small wires.  I found `this one <https://www.amazon.com/dp/B07D25N45F>`__ to work pretty well.

Parts List
----------

The parts list will be updated with each release of the sensor.
I will use Amazon links, but definitely feel free to source them elsewhere.
Just note that if the dimensions change at all, the 3D print would need to be modified.

+-----------------------------------------+-----------+-----------------------------------------------+
| Item                                    | Quantity  | Link                                          |
+=========================================+===========+===============================================+
| Raspberry Pico W                        | 1         | https://www.amazon.com/dp/B0BMP5546H          |
+-----------------------------------------+-----------+-----------------------------------------------+
| DS18x20 temperature sensors             | 1 or 2    | https://www.amazon.com/dp/B09NVFJYPS          |
+-----------------------------------------+-----------+-----------------------------------------------+
| DS18x20 breakout board                  | 1         | https://www.amazon.com/dp/B09NVWNGLQ          |
+-----------------------------------------+-----------+-----------------------------------------------+
| 1.8", 128x160, ST7735r color LCD screen | 1         | https://www.amazon.com/dp/B00LSG51MM          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Female-to-female jumper cables          | 9         | https://www.amazon.com/dp/B0BRTKTV64          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Female-to-male jumper cables            | 2         | https://www.amazon.com/dp/B0BRTKS564          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Female-to-dual-female splitter jumper   | 1         | https://www.amazon.com/dp/B0DSZWFS1V          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Latching switch (debug mode)            | 1         | https://www.amazon.com/gp/product/B086QTH8RW  |
+-----------------------------------------+-----------+-----------------------------------------------+
| Small terminal block                    | 1         | https://www.amazon.com/dp/B0FHGXX6SK          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Small screws (exact sizes TBD)          | A few     | https://www.amazon.com/dp/B081DVZMHH          |
+-----------------------------------------+-----------+-----------------------------------------------+

Data enabled USB Micro for dev
Long power only USB Micro for deploy
USB power plug

Screw sizes:
- Pico: 3 M2x6mm
- Breakout board: 2 M3x5mm
- Screen: 3 M2.3x5mm
- Case: 2 M2.3x10mm

Also note that most of these items listed come as a large amount of that product.
For example, the female splitter product has 10, even though each sensor only needs one wire.

Assembly Steps
--------------

.. important::
    Make sure you use the 3D models, parts list above, code, and these instructions all from the same release.
    Failure to do so may result in parts not fitting or incompatible code.

Gathering Materials
*******************

.. todo:: Add links to the model back on the repo

- Select a specific release of the sensor repo.
- Grab the 3D models from the repo at that point.
- Also order any needed parts from the parts list above.
- Then collect the code from that same release.

First Steps
***********

- Generate a serial number for this box.  Maybe use the same labels as for the wires.  Need to add this to a list of serial numbers :)
- Generate AND SAVE a new token named after the box serial number (Add instructions!)
- Print the base and lid
- Test the screen, breakout board, and pico, checking that the screw holes line up properly

.. _installing_the_pico:

Installing the Debug Switch
***************************

The 3D printed box has a premade hole on the side, and the switch should mount easily.

- Unscrew the mounting nut and slide the switch through from the inside
- Firmly screw on the nut to mount the switch
- Get a small terminal block and fully unscrew both screw terminals
- For now, I'm thinking I'll just trim off the bottom pins, but maybe I'll use them to mount, we'll see
- Take the male ends of the two male-to-female jumper wires, and pair each end with one of the strands of wire coming from the switch
- Fully plunge a switch wire and a jumper wire into one of the terminals and screw it down firmly, pulling slightly to ensure both cables are secure
- Repeat for the other switch wire and jumper

Flashing the Pico
*****************

- Flash the Pico with MicroPython - I'm using 1.27.0 because that's what Thonny currently defaults to -- need to do this early before screwing in the pico

Temperature Sensor(s)
*********************

The temperature sensor will work with either one or two temperature sensors connected through the same breakout board and GPIO pin.

- Use the wire strippers on the temperature sensor(s) to trim back the black covering
- Strip the wires using the 22 gauge slot to about a half inch of exposed wire to give a good amount to hold in the sensor
- Unscrew the breakout board terminal screws to open the ports, then screw the sensor(s) wires into the sensor breakout board tightly (yellow DAT, red VCC, black GND)
- Add jumper cables to the sensor, preferably brown ground, and yellow for data, and then one of the wire splitter ends on the vcc

.. important::
    If you are adding a new temperature sensor to the pool of known sensors, there are a couple extra steps, and this is the right time to do them!
    See the :ref:`adding_a_new_sensor` section for more information there.

Installing the Pico
*******************

- Attach 7 female-to-female jumper wires to Pico GP21 - GP16, which will all wire to the screen
- Attach the female ends of the jumper wires coming from the debug switch terminal block - one to the Pico GP22 and one to Pico GND
- Attach the central end of the wire splitter to the 3V3 pin on the Pico
- Screw in Pico with 3 M2x6mm screws

Installing the Sensor Breakout Board
************************************

- Feed sensors wires from inside through to the outside
- Screw board into place with 2 M3x5mm screws

.. todo: Create proper wiring diagrams for each component and the whole system

Final Wiring
************

- Attach 7 jumper wires from the Pico to the screen
- Attach the VCC splitter end to the screen
- Attach the 2 remaining sensor wires to the pico (sensor DAT to GP28, sensor GND to GND)

First System Test
*****************

- Make sure debug switch is engaged
- Open Thonny on the computer
- Plug in the temperature sensor using the data-enabled USB micro cable
- Open the file sidebar and browse for the code stored locally on your machine
- For each of these: config.py, sensing.py, main.py and st7735.py, right click and choose "Upload to /" to copy them to the Pico root folder
- Open the config.py file on the Pico itself and update the attached sensors, wifi network information, and GitHub token
- With the debugging switch on, execute sensing.py and see what happens

Final Steps
*****************

- Screw screen to lid using 3 M2.3x5mm screws
- Snap lid into place and screw together using 2 M2.3x10mm screws
- Disable debug switch and plug back in to ensure it's running well after assembly
- Deploy to wherever you want
- Once you are satisfied it is working well, make sure to set the sensor to active in the dashboard _data/config.json file
