# noinspection PyPackageRequirements
from machine import Pin, SPI

from st7735 import TFT

from font import FONT

try:
    from temperature.screen_base import ScreenBase
except ImportError:
    ScreenBase = object


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

    # noinspection PyUnusedLocal,PyPep8Naming,PyMissingConstructor
    def __init__(self):
        pin_sck = ScreenTFT.PIN_SCI_SCK
        pin_sda = ScreenTFT.PIN_SDA_MOSI
        spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(pin_sck), mosi=Pin(pin_sda))
        self.tft = TFT(spi, ScreenTFT.PIN_DC, ScreenTFT.PIN_RESET, ScreenTFT.PIN_CS, (128, 160))
        self.tft.initr()
        Pin(ScreenTFT.PIN_LED, Pin.OUT).on()
        self.tft.rgb(False)
        self.tft.fill(TFT.BLACK)

    def fill(self, *args, **kwargs):
        self.tft.fill(*args, **kwargs)

    def circle(self, *args, **kwargs):
        self.tft.circle(*args, **kwargs)

    def text(self, point, text, color, size=1, nowrap=True):
        self.tft.text(point, text, color, FONT, size, nowrap)

    def rect(self, *args, **kwargs):
        self.tft.rect(*args, **kwargs)

    def fillrect(self, *args, **kwargs):
        self.tft.fillrect(*args, **kwargs)

    def hline(self, *args, **kwargs):
        self.tft.hline(*args, **kwargs)

    def vline(self, *args, **kwargs):
        self.tft.vline(*args, **kwargs)
