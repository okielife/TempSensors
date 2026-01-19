from time import sleep

# noinspection PyPackageRequirements
from machine import Pin, reset
from sensing import SensorBox

def main():
    dev_pin = 22  # when developing, jump pin GP22 over to GND
    dev_pin = Pin(dev_pin, Pin.IN, Pin.PULL_UP)
    dev_mode = (dev_pin.value() == 0)
    if dev_mode:
        print("DEV MODE: auto-run disabled")
        r = SensorBox(enable_watchdog=False)
        r.display_dev_mode_warning()
        sleep(2)  # give Thonny time to connect
    else:
        r = SensorBox(enable_watchdog=True)
        r.run()
        # the sensor box run method really should just run forever, and if something hangs, the watchdog should reset,
        # but I guess just in case this gracefully exits somehow, we should reboot it here
        reset()


if __name__ == "__main__":
    main()
