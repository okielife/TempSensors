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

    def __init__(self) -> None:
        self.displayed_messages_for_testing: str = ""

    def fill(self, color: int) -> None:
        raise NotImplementedError

    def circle(self, point: tuple, radius: int, color: int) -> None:
        raise NotImplementedError

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:
        raise NotImplementedError

    def rect(self, point: tuple, size: tuple, color: int) -> None:
        raise NotImplementedError

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        raise NotImplementedError

    def hline(self, point: tuple, length: int, color: int) -> None:
        raise NotImplementedError

    def vline(self, point: tuple, length: int, color: int) -> None:
        raise NotImplementedError

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        raise NotImplementedError
