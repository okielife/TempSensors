class ScreenBase:
    BLACK = 0
    WHITE = 0
    RED = 0
    GREEN = 0
    BLUE = 0
    YELLOW = 0
    GRAY = 0

    WIDTH = 128
    HEIGHT = 160

    # noinspection PyUnusedLocal,PyPep8Naming
    def __init__(self, spi=None, aDC=None, aReset=None, aCS=None, ScreenSize=(128, 160)):
        raise NotImplementedError

    def initr(self):
        raise NotImplementedError

    def rgb(self, _):
        raise NotImplementedError

    def fill(self, color):
        raise NotImplementedError

    def circle(self, point, radius, color):
        raise NotImplementedError

    def text(self, point, text, color, size=1, nowrap=True):
        raise NotImplementedError

    def rect(self, p1, p2, color):
        raise NotImplementedError

    def fillrect(self, point, size, color):
        raise NotImplementedError

    def hline(self, point, length, color):
        raise NotImplementedError

    def vline(self, point, length, color):
        raise NotImplementedError
