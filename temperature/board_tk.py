from time import sleep

from temperature.board_mock import BoardMock


class BoardTk(BoardMock):

    def sleep(self, seconds: float):
        sleep(seconds)
