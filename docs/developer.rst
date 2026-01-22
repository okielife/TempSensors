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
Add tokens
