# This main function/file should only ever be launched from the micropython hardware

# noinspection PyPackageRequirements
from machine import reset

from firmware.board_pico import BoardPico
from firmware.config_pico import ConfigPico
from firmware.screen_tft import ScreenTFT
from firmware.sensing import SensorBox


def main():
    tft = ScreenTFT()
    config = ConfigPico()
    pico = BoardPico()
    sensor = SensorBox(pico, tft, config)
    sensor.run()
    reset()


if __name__ == "__main__":
    main()
