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
 - Add it to the dashboard/_data/config.json file
 - Add a new empty file on the sensor_data branch at data/abcRomHexCode-01-DescriptiveSensorName/_

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

Code Documentation
------------------

.. toctree::
   :maxdepth: 1
   :caption: Controller Board Management:

   code_board_base
   code_board_pico
   code_board_mock
   code_board_tk

.. toctree::
   :maxdepth: 1
   :caption: Runtime Configuration and Data:

   code_config_data
   code_config_base
   code_config_pico
   code_config_mock
   code_config_local_server

.. toctree::
   :maxdepth: 1
   :caption: Main Entry Points:

   code_main
   code_main_tk

.. toctree::
   :maxdepth: 1
   :caption: Display and Screen Classes:

   code_screen_base
   code_screen_mock
   code_screen_tft
   code_screen_tk

.. toctree::
   :maxdepth: 1
   :caption: Primary Sensor Logic:

   code_sensing
