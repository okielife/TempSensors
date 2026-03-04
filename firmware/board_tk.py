from random import randint
from time import sleep

from firmware.board_mock import BoardMock


class BoardTk(BoardMock):

    def __init__(self, watchdog_enabled: bool = False):
        super().__init__(watchdog_enabled)
        self.watchdog_enabled = watchdog_enabled

    def developer_mode(self) -> bool:
        return not self.watchdog_enabled

    def ds18x20_read_temp(self, rom: bytes) -> float:
        """
        Mocks the functionality of reading the temperature for a specific ROM on the one-wire connection.
        If the ds18x20_read_failure flag is active, it will raise an OSError.  If the fixed_temperature_c
        flag was active, then the provided value will be returned.  Otherwise, this chooses a number at
        random
        :param rom:
        :return:
        """
        return randint(-20, 40)

    def sleep(self, seconds: float) -> None:
        sleep(seconds)

    def system_hang(self, seconds: int | None = None) -> None:
        while True:
            sleep(1)

    def run_forever(self) -> bool:
        return True
