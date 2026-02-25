from firmware.screen_base import ScreenBase


class ScreenMock(ScreenBase):
    BLACK = 0
    WHITE = 0
    RED = 0
    GREEN = 0
    BLUE = 0
    YELLOW = 0
    GRAY = 0

    # noinspection PyUnusedLocal,PyPep8Naming,PyMissingConstructor
    def __init__(self):
        self.displayed_messages_for_testing = []

    def fill(self, color):
        pass

    def circle(self, point, radius, color):
        pass

    def text(self, point, text, color, size=1, nowrap=True):
        self.displayed_messages_for_testing.append(text)

    def rect(self, p1, p2, color):
        pass

    def fillrect(self, point, size, color):
        pass

    def hline(self, point, length, color):
        pass

    def vline(self, point, length, color):
        pass
