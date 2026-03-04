from random import randint
from time import sleep

from firmware.board_mock import BoardMock


class BoardTk(BoardMock):
    """
    This class implements the controller API in a way that makes it work well in local development,
    with the Tk screen class being used as the display.  This behavior is similar to the mock class
    used for unit testing, so that is the base class here, but with some specific functions overridden.
    """

    def __init__(self, watchdog_enabled: bool = False):
        """
        Constructs a Tk board controller object.  Developer mode can be triggered by setting the watchdog_enabled arg.
        Setting this True/False allows for developers to see the changes they are making to the screen live.

        :param watchdog_enabled: If True, the system is considered to be in normal run mode.  If False, it is dev mode.
        """
        super().__init__(watchdog_enabled, override_wifi_ssids=["EmeraldWiFi"])
        self.watchdog_enabled = watchdog_enabled

    def developer_mode(self) -> bool:
        """
        Returns whether the board is in developer mode, based solely on the watchdog_enabled arg in the constructor.

        :return: True or False whether the board is in developer mode
        """
        return not self.watchdog_enabled

    def ds18x20_read_temp(self, rom: bytes) -> float:
        """
        Mocks the functionality of reading the temperature for a specific ROM on the one-wire connection.
        For this Tk controller, this function simply chooses a random number to return as the temperature.

        :param rom: Ignored in this implementation
        :return: A random temperature between -20 and +40, in degrees Celsius
        """
        return randint(-20, 40)

    def sleep(self, seconds: float) -> None:
        """
        Sleeps for a specified number of seconds.  Unlike the mock base class, this actually sleeps, so that
        developers can see the actual behavior of the device and screen in real time.

        :param seconds: Number of seconds to sleep
        :return: Nothing
        """
        sleep(seconds)

    def system_hang(self, seconds: int | None = None) -> None:
        """
        Provides a single place for causing the system to "hang" for either an amount of seconds, or forever.

        There are some scenarios where the system may need to hang for a few seconds, such as if an error pops up, and
        you want to hold the sensor for 30 seconds then let the machine reboot.  That way the message may be seen on the
        sensor.  In that case, call this with a positive integer number of seconds and the controller hangs that long.

        There are some scenarios where the system may need to hang forever, such as if the sensor initialization fails
        immediately upon boot.  In that case, call this with no argument, or None.  The controller will hang forever.

        :param seconds: Number of seconds to hang, or None to hang forever
        :return: Nothing
        """
        if seconds is None:
            while True:
                sleep(1)
        else:
            for i in range(seconds):
                sleep(1)

    def run_forever(self) -> bool:
        """
        Returns whether this controller should actually run "forever".  For this Tk hardware board,
        the answer is yes, the sensing system should run continually.

        :return: True
        """
        return True
