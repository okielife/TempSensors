Pinout Diagram
==============

.. _pinout:

.. code-block::

  Looking at the Pico from "above", so that you can see the WiFi antenna
                                       ┏━━━━┓USB CONNECTION
                                 ┌─────┃    ┃─────┐
                        GP0  | 01│     ┗━━━━┛     │40 | VBUS
                        GP1  | 02│                │39 | VSYS
                        GND  | 03│                │38 | GND
                        GP2  | 04│     ╭─╮        │37 | 3V3_EN
                        GP3  | 05│     │ │        │36 | 3V3(OUT)  - SPLIT TO SCREEN VCC and SENSOR VCC
                        GP4  | 06│     ╰─╯        │35 | ADC_VREF
                        GP5  | 07│                │34 | GP28  - SENSOR DAT
       FACTORY RESET -  GND  | 08│                │33 | GND   - SENSOR GND
       FACTORY RESET +  GP6  | 09│    ┌─────┐     │32 | GP27
                        GP7  | 10│    │     │     │31 | GP26
                        GP8  | 11│    │     │     │30 | RUN
                        GP9  | 12│    └─────┘     │29 | GP22
   SCREEN RGB INVERT -  GND  | 13│                │28 | GND
   SCREEN RGB INVERT +  GP10 | 14│                │27 | GP21  - SCREEN LED+
                        GP11 | 15│                │26 | GP20  - SCREEN RESET
                        GP12 | 16│                │25 | GP19  - SCREEN SDA
                        GP13 | 17│                │24 | GP18  - SCREEN SCL
        DEBUG JUMPER -  GND  | 18│                │23 | GND   - SCREEN GND
        DEBUG JUMPER +  GP14 | 19│                │22 | GP17  - SCREEN CS
                        GP15 | 20│                │21 | GP16  - SCREEN A0/DC
                                 └────────────────┘

  Looking at the TFT screen from below, where you can see the SD card slot
   ┌─────────────────────────────────────────────────────────────┐
   │                  ┌─────────────────────────────┐            │ LED-
   │                  │                             │            │ LED+  - PICO GP21
   │                  │                             │            │ SD_CS
   │                  │                             │            │ MOSI
   │                   ╲                            │            │ MISO
   │                    │                           │            │ SCK
   │                    │                           │            │ CS    - PICO GP17
   │                    └───────────────────────────┘            │ SCL   - PICO GP18
   │                                                             │ SDA   - PICO GP19
   │                                                             │ A0    - PICO GP16
   │                                                             │ RESET - PICO GP20
   │                                                             │ NC
   │                                                             │ NC
   │                                                             │ NC
   │                                                             │ VCC   - SPLITTER FROM PICO 3V3
   │                                                             │ GND   - PICO GND
   └─────────────────────────────────────────────────────────────┘
