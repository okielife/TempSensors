Developer Topics
================

These are code related, or very deep topics.

.. _adding_a_new_sensor:

Adding a New Sensor
-------------------

The list of sensors is maintained in the dashboard configuration file: ``dashboard/_data/config.json``.
The DS18x20 sensors utilize a one-wire connection, so to differentiate between sensors, they all have unique identifiers (ROMs).
We keep a hex representation of that ID in order to decide what each sensor is currently monitoring.
To add a new sensor to the list, you need to generate this hex ROM code.
If you are using the custom built MicroPython firmware, you should jump the developer mode pin to ground so the device can be accessed.

Plug the device into the computer and open Thonny.
You should be able to access the REPL shell at the bottom of the program.
Execute this code in that shell, or copy the ``scripts/print_rom.py`` file to the device and run it:

.. code-block::

    import machine, onewire, ds18x20
    print([x.hex() for x in ds18x20.DS18X20(onewire.OneWire(machine.Pin(28))).scan()])

This will print the ROMs for all connected devices (assuming the sensors are connected at pin GP28).
Once these are written down:

 - Add it to the dashboard/_data/config.json file in both the rom hex map and the sensor map, with an "active" key probably set to false initially
 - Add a new empty file on the sensor_data branch at data/abcRomHexCode-01-DescriptiveSensorName/_

Forking the Project
-------------------

The process should be pretty simple to make your own suite of sensors and dashboard.

- Fork the repo
- Create a sensor bot, generate a GH key for it with write access to the forked repo
- Adjust default wifi networks as desired
- Choose a release and build your own device

Building the Custom Firmware
----------------------------

Check out the micropython repo, install tools, add the required files inside ports/rp2/modules, and build it:

- ``git clone git@github.com:micropython/micropython``
- ``git submodule update --init --recursive``
- copy ``main.py`` into ``ports/rp2/modules``
- create ``ports/rp2/modules/firmware`` directory
- copy all supporting files into that firmware directory
- ``sudo apt install gcc-arm-none-eabi``
- ``make BOARD=RPI_PICO_W``
- new firmware will be at ``ports/rp2/modules/build-RPI_PICO_W/firmware.uf2``

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
