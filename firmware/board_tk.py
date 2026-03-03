from time import sleep

from firmware.board_mock import BoardMock


class BoardTk(BoardMock):

    def __init__(self):
        super().__init__(watchdog_enabled=False, continue_running_after_first_iteration=True)
        self.watchdog_enabled = False

    def developer_mode(self) -> bool:
        return not self.watchdog_enabled

    def sleep(self, seconds: float) -> None:
        sleep(seconds)
