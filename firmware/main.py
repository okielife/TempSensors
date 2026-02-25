# This main function/file should only ever be launched from the micropython hardware

# noinspection PyPackageRequirements
from machine import Pin, reset

from time import sleep

from board_pico import BoardPico
from screen_tft import ScreenTFT
from sensing import SensorBox
from config import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN


def main():
    dev_pin = 22  # when developing, jump pin GP22 over to GND
    dev_pin = Pin(dev_pin, Pin.IN, Pin.PULL_UP)
    dev_mode = (dev_pin.value() == 0)

    rgb_invert_pin = 22  # TFT screens are inconsistent with RGB order, so jump pin GP14 to ground to invert blue/red
    rgb_invert_pin = Pin(rgb_invert_pin, Pin.IN, Pin.PULL_UP)
    rgb_invert_mode = (rgb_invert_pin.value() == 0)

    # init the TFT base class to get a terminal first
    tft = ScreenTFT(rgb_invert_mode)

    if dev_mode:
        print("GP22 jumper is connected; device is in developer mode")
        pico = BoardPico(watchdog_enabled=False)
        r = SensorBox(pico, tft, WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN)
        r.enter_dev_mode()
        while True:
            sleep(1)
    else:
        pico = BoardPico(watchdog_enabled=True)
        r = SensorBox(pico, tft, WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN)
        r.run()
        # the sensor box run method really should just run forever, and if something hangs, the watchdog should reset,
        # but I guess just in case this gracefully exits somehow, we should reboot it here
        reset()


if __name__ == "__main__":
    main()
