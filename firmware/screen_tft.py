# noinspection PyPackageRequirements
from machine import Pin, SPI

from firmware.font import FONT
from firmware.screen_base import ScreenBase
from firmware.st7735 import TFT


class ScreenTFT(ScreenBase):
    BLACK = TFT.BLACK
    WHITE = TFT.WHITE
    RED = TFT.RED
    GREEN = TFT.GREEN
    BLUE = TFT.BLUE
    YELLOW = TFT.YELLOW
    GRAY = TFT.GRAY

    PIN_DC = 16
    PIN_CS = 17
    PIN_SCI_SCK = 18
    PIN_SDA_MOSI = 19
    PIN_RESET = 20
    PIN_LED = 21
    PIN_RGB_INVERT = 10  # TFT screens are inconsistent with RGB order, so jump pin GP10 to ground to invert RGB<>BGR

    # noinspection PyUnusedLocal,PyPep8Naming,PyMissingConstructor
    def __init__(self) -> None:
        pin_sck = ScreenTFT.PIN_SCI_SCK
        pin_sda = ScreenTFT.PIN_SDA_MOSI
        spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(pin_sck), mosi=Pin(pin_sda))
        self.tft = TFT(spi, ScreenTFT.PIN_DC, ScreenTFT.PIN_RESET, ScreenTFT.PIN_CS, (128, 160))
        self.tft.initr()
        rgb_invert_pin = Pin(ScreenTFT.PIN_RGB_INVERT, Pin.IN, Pin.PULL_UP)
        rgb_invert_mode = (rgb_invert_pin.value() == 1)
        Pin(ScreenTFT.PIN_LED, Pin.OUT).on()
        self.tft.rgb(rgb_invert_mode)
        self.tft.fill(TFT.BLACK)

    def fill(self, color: int) -> None:
        self.tft.fill(color)

    def circle(self, point: tuple, radius: int, color: int) -> None:
        self.tft.circle(point, radius, color)

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap=True) -> None:
        self.tft.text(point, text, color, FONT, size, nowrap)

    def rect(self, point: tuple, size: tuple, color: int) -> None:
        self.tft.rect(point, size, color)

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        self.tft.fillrect(point, size, color)

    def hline(self, point: tuple, length: int, color: int) -> None:
        self.tft.hline(point, length, color)

    def vline(self, point: tuple, length: int, color: int) -> None:
        self.tft.vline(point, length, color)

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        size = len(qr_bits)
        x_offset = (128 - size * scale) // 2
        for y in range(size):
            for x in range(size):
                if qr_bits[y][x]:
                    starting_x_position = x_offset + x * scale
                    starting_y_position = y_offset + y * scale
                    width = scale
                    height = scale
                    self.fillrect(
                        (starting_x_position, starting_y_position), (width, height),
                        self.WHITE
                    )
