from firmware.screen_base import ScreenBase


class ScreenMock(ScreenBase):
    """
    This class implements the screen API in a mock, nearly empty state, for unit testing purposes
    """

    #: Empty mock Black color definition
    BLACK = 0
    #: Empty mock White color definition
    WHITE = 0
    #: Empty mock Red color definition
    RED = 0
    #: Empty mock Green color definition
    GREEN = 0
    #: Empty mock Blue color definition
    BLUE = 0
    #: Empty mock Yellow color definition
    YELLOW = 0
    #: Empty mock Gray color definition
    GRAY = 0

    def fill(self, color: int) -> None:
        """
        Mock fill method which does nothing

        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def circle(self, point: tuple, radius: int, color: int) -> None:
        """
        Mock circle method which does nothing

        :param point: Unused in this mock class
        :param radius: Unused in this mock class
        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:
        """
        This mock text method simply updates the displayed messages variable with the new text. This allows unit testing
        to ensure the display showed a message to the user under various conditions.

        :param point: Unused in this mock class
        :param text: Unused in this mock class
        :param color: Unused in this mock class
        :param size: Unused in this mock class
        :param nowrap: Unused in this mock class
        :return: Nothing
        """
        self.displayed_messages_for_testing += text

    def rect(self, p1: tuple, p2: tuple, color: int) -> None:
        """
        Mock rect method which does nothing

        :param p1: Unused in this mock class
        :param p2: Unused in this mock class
        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        """
        Mock fillrect method which does nothing

        :param point: Unused in this mock class
        :param size: Unused in this mock class
        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def hline(self, point: tuple, length: int, color: int) -> None:
        """
        Mock hline method which does nothing

        :param point: Unused in this mock class
        :param length: Unused in this mock class
        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def vline(self, point: tuple, length: int, color: int) -> None:
        """
        Mock vline method which does nothing

        :param point: Unused in this mock class
        :param length: Unused in this mock class
        :param color: Unused in this mock class
        :return: Nothing
        """
        pass

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        """
        Mock draw_qr method which does nothing

        :param y_offset: Unused in this mock class
        :param qr_bits: Unused in this mock class
        :param scale: Unused in this mock class
        :return: Nothing
        """
        pass
