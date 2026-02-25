from time import sleep

from firmware.board_mock import BoardMock


class BoardTk(BoardMock):

    def sleep(self, seconds: float):
        sleep(seconds)
