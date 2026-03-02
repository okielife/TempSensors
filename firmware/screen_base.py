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
    def __init__(self):
        self.displayed_messages_for_testing: list[str] = []

    def fill(self, color) -> None:
        raise NotImplementedError

    def circle(self, point: tuple, radius: int, color) -> None:
        raise NotImplementedError

    def text(self, point: tuple, text: str, color, size: int = 1, nowrap: bool = True) -> None:
        raise NotImplementedError

    def rect(self, p1: tuple, p2: tuple, color) -> None:
        raise NotImplementedError

    def fillrect(self, point: tuple, size: tuple, color) -> None:
        raise NotImplementedError

    def hline(self, point: tuple, length: int, color) -> None:
        raise NotImplementedError

    def vline(self, point: tuple, length: int, color) -> None:
        raise NotImplementedError

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        raise NotImplementedError
