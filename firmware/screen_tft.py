# noinspection PyPackageRequirements
from machine import Pin, SPI

from firmware.font import FONT
from firmware.screen_base import ScreenBase
from firmware.st7735 import TFT


class ScreenTFT(ScreenBase):
    """
    This class implements the screen API, specifically for hardware, ST7735 TFT usage inside MicroPython.
    This class actually communicates with the screen via the st7735 driver, providing a drawing surface
    that is actually shown to the user.
    """
    #: Black color definition copied in from the st7735 driver class
    BLACK = TFT.BLACK
    #: White color definition copied in from the st7735 driver class
    WHITE = TFT.WHITE
    #: Red color definition copied in from the st7735 driver class
    RED = TFT.RED
    #: Green color definition copied in from the st7735 driver class
    GREEN = TFT.GREEN
    #: Blue color definition copied in from the st7735 driver class
    BLUE = TFT.BLUE
    #: Yellow color definition copied in from the st7735 driver class
    YELLOW = TFT.YELLOW
    #: Gray color definition copied in from the st7735 driver class
    GRAY = TFT.GRAY

    #: Pico pin connected to screen DC terminal
    PIN_DC = 16
    #: Pico pin connected to screen CS terminal
    PIN_CS = 17
    #: Pico pin connected to screen SCI/SCK terminal
    PIN_SCI_SCK = 18
    #: Pico pin connected to screen SDA/MOSI terminal
    PIN_SDA_MOSI = 19
    #: Pico pin connected to screen RESET terminal
    PIN_RESET = 20
    #: Pico pin connected to screen LED+ terminal
    PIN_LED = 21

    #: Pico pin used to trigger RGB invert mode if jumped to GND
    PIN_RGB_INVERT = 10

    def __init__(self) -> None:
        """
        Constructs a hardware (TFT, st7735r) display class.  Upon construction, this class checks the RGB
        invert pin to determine whether to reverse RGB<>BGR to accommodate screen inconsistencies.
        """
        super().__init__()
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
        """
        This function uses the st7735 driver to fill the draw surface with the provided color.

        :param color: The color to fill
        :return: Nothing
        """
        self.tft.fill(color)

    def circle(self, point: tuple, radius: int, color: int) -> None:
        """
        This function uses the st7735 driver to draw a hollow circle at the given point and radius, with the given color

        :param point: Center point of the circle
        :param radius: Radius of the circle
        :param color: Color of the circle
        :return: Nothing
        """
        self.tft.circle(point, radius, color)

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap=True) -> None:
        """
        This function uses the st7735 driver to render text at the given point with the given color and size

        :param point: Top left point of the text string
        :param text: The text string to render
        :param color: The text color
        :param size: The size of the font
        :param nowrap: A flag to determine whether to not wrap text
        :return: Nothing
        """
        self.tft.text(point, text, color, FONT, size, nowrap)

    def rect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function uses the st7735 driver to draw a rectangle at the given point and size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle outline color
        :return: Nothing
        """
        self.tft.rect(point, size, color)

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function uses the st7735 driver to draw a filled rectangle at the given point, size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle fill color
        :return: Nothing
        """
        self.tft.fillrect(point, size, color)

    def hline(self, point: tuple, length: int, color: int) -> None:
        """
        This function uses the st7735 driver to draw a horizontal line at the given point, length and color

        :param point: Left point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        self.tft.hline(point, length, color)

    def vline(self, point: tuple, length: int, color: int) -> None:
        """
        This function uses the st7735 driver to draw a vertical line at the given point, length and color

        :param point: Top point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        self.tft.vline(point, length, color)

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        """
        This function uses the st7735 to render a set of bits as black and white rectangles, such as a QR code.

        :param y_offset: The top margin above the rendered bits
        :param qr_bits: The bits to render, as a list of lists of ones and zeroes
        :param scale: The render scale to make it show up easier on the screen
        :return: Nothing
        """
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
