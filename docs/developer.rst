Developer Topics
================

These are code related, or very deep topics.

.. _adding_a_new_sensor:

Adding a New Sensor
-------------------

The dashboard branch needs to know about all sensors that might be deployed.
Need to:

 - Make sure you've flashed MicroPython on it as described in the :ref:`installing_the_pico` section
 - Connect up the
 - Capture the ROM using the temperature/print_rom.py
 - Add it to the _data/config.json file
 - Add a new blank file at _posts/ROMABC123/CurrentNameOfTheSensor.txt

Forking the Project
-------------------

If you want to make your own suite of sensors and dashboard.
Fork the dashboard, maybe I'll make it a template
You'll need a new bot user, then you'll need your own token, I'll have instructions for tokens here
Add tokens

Building the Custom Firmware
----------------------------

Check out the micropython repo, install tools, add the required files inside ports/rp2/modules, and build it:

- git clone git@github.com:micropython/micropython
- git submodule update --init --recursive
- copy main.py into ports/rp2/modules
- create ports/rp2/modules/firmware directory
- copy all supporting files into that firmware directory
- sudo apt install gcc-arm-none-eabi
- make BOARD=RPI_PICO_W
- new firmware will be at ports/rp2/modules/build-RPI_PICO_W/firmware.uf2
