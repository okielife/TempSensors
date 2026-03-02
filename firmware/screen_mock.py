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

    def fill(self, color: int) -> None:
        pass

    def circle(self, point: tuple, radius: int, color: int) -> None:
        pass

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:
        self.displayed_messages_for_testing.append(text)

    def rect(self, p1: tuple, p2: tuple, color: int) -> None:
        pass

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        pass

    def hline(self, point: tuple, length: int, color: int) -> None:
        pass

    def vline(self, point: tuple, length: int, color: int) -> None:
        pass

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        pass
