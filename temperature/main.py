# This main function/file should only ever be launched from the micropython hardware

# noinspection PyPackageRequirements
from machine import Pin, reset

from time import sleep

from board_pico import BoardPico
from screen_tft import ScreenTFT
from sensing import SensorBox


def main():
    dev_pin = 22  # when developing, jump pin GP22 over to GND
    dev_pin = Pin(dev_pin, Pin.IN, Pin.PULL_UP)
    dev_mode = (dev_pin.value() == 0)

    # init the TFT base class to get a terminal first
    tft = ScreenTFT.default_construct()

    if dev_mode:
        board = BoardPico(watchdog_enabled=False)
        print("DEV MODE: auto-run disabled")
        r = SensorBox(tft, board)
        r.display_dev_mode_warning()
        sleep(2)  # give Thonny time to connect
    else:
        board = BoardPico(watchdog_enabled=True)
        r = SensorBox(tft, board)
        r.run()
        # the sensor box run method really should just run forever, and if something hangs, the watchdog should reset,
        # but I guess just in case this gracefully exits somehow, we should reboot it here
        reset()


if __name__ == "__main__":
    main()
