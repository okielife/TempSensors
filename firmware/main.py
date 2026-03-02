# This main function/file should only ever be launched from the micropython hardware

# noinspection PyPackageRequirements
from machine import reset

from board_pico import BoardPico
from config_pico import ConfigPico
from screen_tft import ScreenTFT
from sensing import SensorBox


def main():
    tft = ScreenTFT()
    config = ConfigPico()
    pico = BoardPico()
    sensor = SensorBox(pico, tft, config)
    sensor.run()
    reset()


if __name__ == "__main__":
    main()
