Building Your Own
=================

This covers the assembly of one of these temperature sensors

Required Tools
**************

There are a few tools and items which will need to be purchased once and used for all future sensor builds.

- The primary one is the 3D printer itself.
  I am getting by with a very small hobby 3D printer that I got off of Amazon `here <https://www.amazon.com/dp/B0CMHM6XQG>`__.
  It has a very small print area, which has forced me to rethink the design multiple times, for better or for worse.
- You will need some very small screw drivers, both flat and phillips, and both in the 1-3mm range.
  A set like `this <https://www.amazon.com/Screwdriver-Flathead-Phillips-Screwdrivers-Computer/dp/B0BMWQNMPS/>`__ is great.
- You will also want some wire strippers for small wires.  I found `this one <https://www.amazon.com/dp/B07D25N45F>`__ to work pretty well.
- You will need one data-transfer-enabled USB micro cable to upload the firmware to the Pico.  One example is this: https://www.amazon.com/dp/B074VM7SMM.  If the cable is a power-only cable, it will not connect to the computer properly.  While it's not a 100% guarantee, the general consensus is that if the micro port has the USB trident logo on it, it should be a data cable.  Charge-only cables rarely have this.

Parts List
**********

The parts list is updated with each release of the sensor.
This table shows Amazon links, but definitely please source them as you see fit.
Just note that if the dimensions change at all, the 3D print might need to be modified.

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
| Female-to-dual-female splitter jumper   | 1         | https://www.amazon.com/dp/B0DSZWFS1V          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Small surface button switch (reset)     | 1         | https://www.amazon.com/gp/product/B01J9KO7DC  |
+-----------------------------------------+-----------+-----------------------------------------------+
| Jumpers for dev mode and RGB invert     | 1         | https://www.amazon.com/dp/B0FHGXX6SK          |
+-----------------------------------------+-----------+-----------------------------------------------+
| Small screws (exact sizes below)        | A few     | https://www.amazon.com/dp/B081DVZMHH          |
+-----------------------------------------+-----------+-----------------------------------------------+
| USB Micro cable and block (size to fit) | 1         | https://www.amazon.com/dp/B07P5CP5KP          |
+-----------------------------------------+-----------+-----------------------------------------------+

A single case will require these screw sizes and quantities:

- Pico mount to box: 3 M2x6mm
- Breakout board mount to box: 2 M3x5mm
- Screen mount to lid: 3 M2.3x5mm
- Case to lid: 2 M2.3x10mm

Notes:

- Most of the item links above contain a bulk amount of that product, so each purchase would support multiple/many sensor boxes.
  For example, the female splitter shown above is a bag of 10, even though each sensor box only needs one.
- If you feel like you need to mount the sensor to the front of the fridge, you might need to get creative.
  One option is to use magnets like `these <https://www.amazon.com/dp/B072KDBJWC>`__.  
  Another option would be to use a metal bracket hanging on the door.
  In many cases, you may be able to just set the sensor on top of the fridge.

.. important::
    Make sure you choose a single release of the project, and use the 3D models, parts list, firmware, and instructions all from that *same* release.
    Failure to do so may result in parts not fitting or incompatible code.

Gathering Materials
*******************

- Select a specific release of the sensor repo from `here <https://github.com/okielife/TempSensors/releases>`__.
- The releases will have all necessary files: 3D models, assembly instructions, and firmware; so download all of them.
- Order any needed parts from the parts list above.

.. _first_steps:

First Steps
***********

- Print the 3D models provided in the release asset using your 3D printer workflow, or perhaps even order a print from online

.. todo::
   Add a picture of the 3D printed boxes alone

- Test fit the screen, breakout board, and Pico, checking that the screw holes line up properly

.. todo::
   Add a picture of the pico, sensor board, and screen all test fitted into the box

- Generate a serial number for this box.  Either use permanent marker or use a sticker to mark it on the box.  A list of known serial numbers is currently stored in the `dashboard config file <https://github.com/okielife/TempSensors/blob/main/dashboard/_data/config.json>`__.

.. todo::
   Add a picture of the serial number sticker on the box

- Generate AND SAVE a new token named after the box serial number

  - If not already done, create a GitHub user to be the "bot" pushing data to the repo
  - Make sure that bot is invited to collaborate in the repo so that it will have write access
  - Make sure the new bot user is currently logged into GitHub
  - Go to https://github.com/settings/tokens/new
  - Choose your preferred expiration time
  - Choose only ``repo->public_repo`` access so that it can post results
  - Select ``Generate Token``
  - Save the token text somewhere safe, preferably a secure local file.  The token will be secret forever after leaving that GitHub page.  During provisioning, the phone or computer connected to the sensor will need that token and will not have internet access.

.. _installing_the_pico:

Wiring Details
**************

A description of the wiring connections, or "pinout", is available on the online docs as well as provided as a release asset PDF along with the PDF instruction manual.
Throughout these instructions, consult this :ref:`pinout <pinout>` for all wiring details.
It may be helpful to open it in a new tab, or even better, in split view, next to these instructions.

Flashing the Pico
*****************

- This is easier to do before mounting the Pico.  If you did already mount the Pico, you can use a small hole in the box to access the BOOTSEL button.

.. todo::
   Add picture showing the hole in the box for flashing access

- There is a custom MicroPython firmware build available as a sensor release asset, with all sensor code pre-frozen into the firmware.
- The preferred approach is to flash that directly onto the Pico, as no other steps or programs are necessary with a computer.
- Hold the BOOTSEL button on the Pico while plugging it into the computer with a data-transfer-capable USB micro cable and it will mount a drive on the system named RPI-RP2.  
- Copy the custom .uf2 firmware file onto the new mounted RPI-RP2 drive.
- Once copied, the process is complete and the Pico will reboot.

.. important::
   The Pico storage is actually divided into a bootloader section, a firmware section, and a filesystem section.
   Flashing the Pico with the custom MicroPython firmware here does **not** erase the filesystem section, which could leave files lying around.
   If you are using a Pico which has been through multiple applications, you may want to consider wiping the flash entirely, both firmware and filesystem..
   You can find methods to reset the board's filesystem section online.  

Installing the Factory Reset Switch
***********************************

The sensor boxes have a button to allow re-provisioning.
This can be useful if the Wi-Fi ever changes, or the GitHub token needs to change.
Hold this button while plugging in the system, and it should clear the custom runtime configuration and start fresh with a new provisioning experience.

The 3D printed box has a premade hole on the back, with a little bracket to mount the switch from the inside.
This bracket design and mount process have not been refined, so it can be a little finicky.
As of version 3:5 of the case, I feel OK about it, but I look forward to polishing it up.

The button is on the back, as seen here from the back external view and the top internal view:

.. todo::
   Get better pictures for sure.

..  .. image:: images/reset_button_external.jpg
..  :alt: External view of the factory reset button
..  :width: 45%

.. image:: images/reset_button_internal.jpg
   :alt: Internal view of the factory reset button
   :width: 41%
   :align: center

Basically just take the switch and try to pivot it side to side while pushing until it seats itself in the slot.
A close up view may help:

.. image:: images/reset_button_closeup.jpg
   :alt: Closeup view of the factory reset button
   :width: 80%
   :align: center

But for that picture to help, it would require better photography skills. :)

Temperature Sensor(s)
*********************

.. todo::
   Add picture of the temperature sensors themselves, maybe showing the sensor and the terminated wires

DS18x20 temperature sensors work on a one-wire design, where multiple sensors can communicate through a single data wire.
This temperature sensor project will work with either one or two of these temperature sensors connected through a single breakout board and a single GPIO pin.
Brand new sensor wires may be pre-stripped and ready to go, but if not, you may need to prep the wires.
Here are some tips:

- Use the wire strippers on the temperature sensor(s) to trim back the black covering
- Strip the wires using a 22 gauge slot to about a quarter inch of exposed wire to give a good amount to hold in the sensor

  - You do *not* want too much wire exposed, as accidental short circuits here will cause a warm box and a risk.
  - It seems finicky at first, but it is very possible to get a clean wire strip and end up with nice terminated ends to put in the screw terminals.
  - Also it would be ideal to get all three wires stripped very close to the same position next to each other, so there is no unnecessary stress on each wire pulling or pushing on the other ends.

.. important::
   This next step is **by far** the most finicky, frustrating, and difficult part of the whole build.
   The wires will **not** want to get into the screw terminals, and even if they do, they will not want to stay.
   Just *Stay Determined!*
   Take enough tries and time to get the wires in firmly, without any excess exposed wire that could cause a short circuit.
   The screw terminals should be screwed down sufficiently tight, as these screws not only provide the electrical connection, but also the mechanical connection to hold the wires in place.

You are looking for the terminals to look something like this image:

.. todo::
   Get a picture showing the wires just after screwing them into the terminals.

- Unscrew the breakout board terminal screws to open the ports, then screw the sensor(s) wires into the sensor breakout board tightly

  - If you are using two sensors, you will just have to get both wires inserted into each terminal together, which is a challenge.
  - Yellow to DAT, red to VCC, and black to GND
  - It may be helpful to use a desktop stand that has alligator clips to hold the wires together as you insert them and screw the terminals in.

.. todo::
   Get a picture of the breakout board with the wires attached

- Add jumper cables to the sensor breakout board pins:

  - Female to female for the ground and data, preferably brown for ground and yellow for data
  - One of the ends of female-female-female wire splitter on the vcc

.. important::
    If you are adding a new temperature sensor to the pool of known sensors, there are a couple extra steps, and this is the right time to do them!
    See the :ref:`adding_a_new_sensor` section for more information there.

Installing the Pico
*******************

- Attach 7 female-to-female jumper wires to Pico GP21 - GP16, which will all wire to the screen
- Assuming you are starting with a debugging session (you are), put a jumper from pin GP14 to ground
- Attach the central end of the wire splitter to the 3V3 pin on the Pico
- Attach the data and ground jumper wires from the sensor breakout board to the Pico according to the pinout

At this point, the Pico should look something like this:

.. todo::
   Update the picture here to show it without the reset switch wires.

.. image:: images/pico_with_wires.jpg
   :alt: Quick snapshot of a Pico with wires connected

- Place the Pico pins up with the USB port facing the power cable access hole in the case
- Screw in Pico with 3 M2x6mm screws

.. todo::
   Now get a picture with it actually mounted.  Maybe show the USB port through the hole.

Installing the Sensor Breakout Board
************************************

- Feed sensor wires from inside through to the outside

.. todo::
   Maybe a diagram showing the wires being fed through the hole in the box.

- Screw board into place with 2 M3x5mm screws

.. todo::
   Fix this next picture

This image needs to be replaced, but it basically shows the sensor breakout board wiring.  (It shows the board installed without the Pico under it and it's unfocused)

.. image:: images/sensor_breakout.jpg
   :alt: An image of the breakout board with sensor and jumpers attached.
   :width: 75%
   :align: center

If any holes are not aligned, you may have received an incompatible part or ordered the wrong materials for this case design.

Final Wiring
************

- Attach 7 jumper wires from the Pico to the screen
- Attach the VCC splitter end to the screen
- Attach the 2 reset switch wires to the Pico GP6 and GND pins

Manually Copying Firmware Files
*******************************

- If you are running with the new custom firmware, you can **skip** this step entirely and move on to :ref:`provisioning <provisioning>`.
  No files need to be transferred as they were all pre-frozen into the custom firmware.
- Make sure debug jumper is connected
- Open Thonny on the computer
- Plug in the temperature sensor using the data-enabled USB micro cable

  - Open the file sidebar and browse for the code stored locally on your machine
  - Copy the main.py file from the repo to the Pico root by right clicking and choosing "Upload to /"
  - Create a firmware directory on the Pico file system
  - Double click that folder on the Pico to focus on it
  - Then on each of the following files, right click on the local file and choose "Upload to /firmware/"

    - board_base.py
    - board_pico.py
    - config_base.py
    - config_data.py
    - config_pico.py
    - font.py
    - screen_base.py
    - screen_tft.py
    - sensing.py
    - st7735.py
    - __init__.py

- The sensor box firmware is now set up and ready to be provisioned.

.. _provisioning:

.. important::
   Before beginning the provisioning step, make sure to get the GitHub token created above and have it ready to paste in.
   While connected to the Pico's own network for provisioning, you will not have internet access.

Provisioning the Runtime Configuration
**************************************

  - Plug in the Pico, either to the computer or a normal power source. 
    (It doesn't matter, as file transfer is complete at this point.)
  - The sensor box should launch a small Wi-Fi server and HTTP server
  - The Wi-Fi network should be listed on the screen, so connect to that from a device (phone or laptop)
  - Once connected to that network, scan the QR code on the screen, or browse to http://192.168.4.1 (not https!)
  - Paste in the GitHub token generated in the :ref:`first steps <first_steps>` above.
  - If the sensor should connect to a Wi-Fi network not listed, add the credentials there
  - Once submitted, the sensor should reboot and go into debug mode

RGB Check
*********

Some of the screens I have purchased have the RGB switched, even with the same code and apparent hardware.
A jumper can be placed to reverse the order if it is backwards.

.. todo::
   Image of jumper for RGB

- When booting up the device, take note of the POST screen as shown in :ref:`the figure below <tk-post>`.  The SCREEN section shows RGB, with R in red, G in green, and B in blue.
- If those are reversed, then place a jumper between GP10 and ground.
- Reboot and verify the R is red on the POST screen.
- Once everything is working well, you are ready to wrap the build!

.. _tk-post:

.. figure:: images/tk_post_success.png
   :alt: Tk window showing POST screen
   :align: center
   :scale: 50

Final Steps
*****************

- Screw screen to lid using 3 M2.3x5mm screws
- Take out debug jumper that was connecting pin 14 to ground
- Snap lid into place and screw together using 2 M2.3x10mm screws - push in hard at first to break through plastic, then screw in
- Deploy to wherever you want, hanging sensors inside fridge/freezer doors.
- Once you are satisfied it is working well, make sure to set the sensor to active in the dashboard/_data/config.json file

.. todo::
   Image of deployed sensor box with wires in the fridge/freezer
