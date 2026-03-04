# This main function/file should only ever be launched from the micropython hardware

# noinspection PyPackageRequirements
from machine import reset

from firmware.board_pico import BoardPico
from firmware.config_pico import ConfigPico
from firmware.screen_tft import ScreenTFT
from firmware.sensing import SensorBox


def main():
    """
    This is the main entry point for the firmware.  After boot, this main.py file (frozen) is executed, which
    calls this function.  This function is executed only in MicroPython, and constructs hardware based screen,
    configuration, and controller board, before passing it to the sensor box class to run.  If anything happens
    to cause control to return from the sensor.run method, this simply calls reset() and tries again.

    :return: Nothing
    """
    tft = ScreenTFT()
    config = ConfigPico()
    pico = BoardPico()
    sensor = SensorBox(pico, tft, config)
    sensor.run()
    reset()


if __name__ == "__main__":
    main()
