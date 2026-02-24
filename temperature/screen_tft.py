# noinspection PyPackageRequirements
from machine import Pin, SPI

from st7735 import TFT

from font import FONT
from screen_base import ScreenBase


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

    # noinspection PyUnusedLocal,PyPep8Naming
    def __init__(self, spi=None, aDC=None, aReset=None, aCS=None, ScreenSize=(128, 160)):
        super().__init__(spi, aDC, aReset, aCS, ScreenSize)
        self.tft = TFT(spi, aDC, aReset, aCS, ScreenSize)

    @classmethod
    def default_construct(cls) -> 'ScreenTFT':
        spi = SPI(
            0,
            baudrate=20_000_000,
            polarity=0,
            phase=0,
            sck=Pin(cls.PIN_SCI_SCK),
            mosi=Pin(cls.PIN_SDA_MOSI)
        )
        screen = cls(
            spi,
            aDC=cls.PIN_DC,
            aReset=cls.PIN_RESET,
            aCS=cls.PIN_CS,
            ScreenSize=(cls.WIDTH, cls.HEIGHT)
        )
        screen.tft.initr()
        Pin(cls.PIN_LED, Pin.OUT).on()
        screen.tft.rgb(False)
        screen.tft.fill(TFT.BLACK)
        return screen

    def initr(self):
        self.tft.initr()

    def rgb(self, *args, **kwargs):
        self.tft.rgb(*args, **kwargs)

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
