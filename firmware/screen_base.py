class ScreenBase:
    """
    This class defines the screen API, which is uniform among all displays that can be passed to the sensor code.
    This defines methods for drawing text and shapes on a surface, whether real or emulated.
    """

    #: Black color definition that should be overridden in derived class implementations
    BLACK = 0
    #: White color definition that should be overridden in derived class implementations
    WHITE = 0
    #: Red color definition that should be overridden in derived class implementations
    RED = 0
    #: Green color definition that should be overridden in derived class implementations
    GREEN = 0
    #: Blue color definition that should be overridden in derived class implementations
    BLUE = 0
    #: Yellow color definition that should be overridden in derived class implementations
    YELLOW = 0
    #: Gray color definition that should be overridden in derived class implementations
    GRAY = 0

    def __init__(self) -> None:
        """
        Constructs a base class instance, which simply creates a string that can be used to check for printed messages.
        """
        self.displayed_messages_for_testing: str = ""

    def fill(self, color: int) -> None:
        """
        This function fills the draw surface with the provided color.

        :param color: The color to fill
        :return: Nothing
        """
        raise NotImplementedError

    def circle(self, point: tuple, radius: int, color: int) -> None:
        """
        This function draws a hollow circle at the given point and radius, with the given color

        :param point: Center point of the circle
        :param radius: Radius of the circle
        :param color: Color of the circle
        :return: Nothing
        """
        raise NotImplementedError

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:
        """
        This function renders text at the given point with the given color and size

        :param point: Top left point of the text string
        :param text: The text string to render
        :param color: The text color
        :param size: The size of the font
        :param nowrap: A flag to determine whether to not wrap text
        :return: Nothing
        """
        raise NotImplementedError

    def rect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function draws a hollow rectangle at the given point and size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle outline color
        :return: Nothing
        """
        raise NotImplementedError

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function draws a filled rectangle at the given point and size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle fill color
        :return: Nothing
        """
        raise NotImplementedError

    def hline(self, point: tuple, length: int, color: int) -> None:
        """
        This function draws a horizontal line at the given point, with the given length and color

        :param point: Left point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        raise NotImplementedError

    def vline(self, point: tuple, length: int, color: int) -> None:
        """
        This function draws a vertical line at the given point, with the given length and color

        :param point: Top point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        raise NotImplementedError

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        """
        This function can render a set of bits as black and white, such as a QR code.

        :param y_offset: The top margin above the rendered bits
        :param qr_bits: The bits to render, as a list of lists of ones and zeroes
        :param scale: The render scale to make it show up easier on the screen
        :return: Nothing
        """
        raise NotImplementedError
