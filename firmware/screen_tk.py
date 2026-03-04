from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

from firmware.font import FONT
from firmware.screen_base import ScreenBase


def _rgb_to_565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def _color565_to_rgb(color: int) -> tuple:
    r = (color >> 11) & 0x1F
    g = (color >> 5) & 0x3F
    b = color & 0x1F
    # Expand to 8-bit
    r = (r * 255) // 31
    g = (g * 255) // 63
    b = (b * 255) // 31
    return r, g, b


class ScreenTk(ScreenBase):
    """
    This class implements the screen API, specifically for development purposes.  A Tk window is instantiated, which
    directly mimics an actual TFT screen by using a Pillow draw surface.  This code is to be instantiated only in
    development mode, as it will not work in MicroPython, and also not on headless CI.
    """
    #: Black color definition custom-built to work with the Tk interface
    BLACK = _rgb_to_565(0, 0, 0)
    #: White color definition custom-built to work with the Tk interface
    WHITE = _rgb_to_565(255, 255, 255)
    #: Red color definition custom-built to work with the Tk interface
    RED = _rgb_to_565(255, 0, 0)
    #: Green color definition custom-built to work with the Tk interface
    GREEN = _rgb_to_565(0, 255, 0)
    #: Blue color definition custom-built to work with the Tk interface
    BLUE = _rgb_to_565(0, 0, 255)
    #: Yellow color definition custom-built to work with the Tk interface
    YELLOW = _rgb_to_565(255, 255, 0)
    #: Gray color definition custom-built to work with the Tk interface
    GRAY = _rgb_to_565(128, 128, 128)

    def __init__(self) -> None:
        """
        Constructs a Tk window application that can be passed to the sensor code inside a Python environment.
        Upon construction, this class creates a Tk root window of the exact size as the hardware screen, a canvas
        widget, and an image to draw on. This code uses the same font as the hardware object so that the Tk version
        really matches the hardware version very well.
        """
        super().__init__()
        self.closed = False
        self.width, self.height = 128, 160
        self.scale = 2  # 1 = real size, 2 = double, etc.

        self.image = Image.new("RGB", (128, 160), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

        self.root = tk.Tk()
        self.root.title("TFT Emulator")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        self._photo = ImageTk.PhotoImage(self.image)
        self._image_id = self.canvas.create_image(0, 0, anchor="nw", image=self._photo)

        self._show()

    def _on_close(self) -> None:
        self.closed = True
        self.root.destroy()

    def fill(self, color: int) -> None:
        """
        This function uses Pillow to fill the draw surface with the provided color.

        :param color: The color to fill
        :return: Nothing
        """
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)
        self._show()

    def circle(self, point: tuple, radius: int, color: int) -> None:
        """
        This function uses Pillow to draw a hollow circle at the given point and radius, with the given color

        :param point: Center point of the circle
        :param radius: Radius of the circle
        :param color: Color of the circle
        :return: Nothing
        """
        x_center, y_center = point
        x_min, x_max = x_center - radius, x_center + radius
        y_min, y_max = y_center - radius, y_center + radius
        c = _color565_to_rgb(color)
        self.draw.ellipse((x_min, y_min, x_max, y_max), outline=c)

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:
        """
        This function uses Pillow to render text at the given point with the given color and size

        :param point: Top left point of the text string
        :param text: The text string to render
        :param color: The text color
        :param size: The size of the font
        :param nowrap: A flag to determine whether to not wrap text
        :return: Nothing
        """
        x: int = point[0]
        y: int = point[1]
        cw: int = FONT.width
        ch: int = FONT.height
        start: int = FONT.start
        end: int = FONT.end
        data: bytearray = FONT.data
        c = _color565_to_rgb(color)

        for ch_i in text:
            code = ord(ch_i)

            if code < start or code > end:
                x += cw * size + size
                continue

            glyph_index = (code - start) * cw

            for col in range(cw):
                column_bits = data[glyph_index + col]

                for row in range(ch):
                    if column_bits & (1 << row):
                        px = x + col * size
                        py = y + row * size
                        self.draw.rectangle(
                            (px, py, px + size - 1, py + size - 1),
                            fill=c
                        )

            x += cw * size + size  # inter-character spacing

            if not nowrap and x >= self.width:
                x = point[0]
                y += ch * size + size

        self._show()

    def rect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function uses Pillow to draw a rectangle at the given point and size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle outline color
        :return: Nothing
        """
        x, y = point
        w, h = size
        c = _color565_to_rgb(color)
        self.draw.rectangle((x, y, x + w, y + h), outline=c)
        self._show()

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        """
        This function uses Pillow to draw a filled rectangle at the given point, size, with the given color

        :param point: Top left point of the rectangle
        :param size: The size (width, height) of the rectangle box
        :param color: The rectangle fill color
        :return: Nothing
        """
        x, y = point
        w, h = size
        c = _color565_to_rgb(color)
        self.draw.rectangle((x, y, x + w, y + h), fill=c)
        self._show()

    def hline(self, point: tuple, length: int, color: int) -> None:
        """
        This function uses Pillow to draw a horizontal line at the given point, length and color

        :param point: Left point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        x, y = point
        c = _color565_to_rgb(color)
        self.draw.line((x, y, x + length, y), fill=c)
        self._show()

    def vline(self, point: tuple, length: int, color: int) -> None:
        """
        This function uses Pillow to draw a vertical line at the given point, length and color

        :param point: Top point of the horizontal line
        :param length: Length of the line to draw
        :param color: Line color
        :return: Nothing
        """
        x, y = point
        c = _color565_to_rgb(color)
        self.draw.line((x, y, x, y + length), fill=c)
        self._show()

    def _show(self) -> None:
        if self.closed:
            return

        if self.scale != 1:
            display_image = self.image.resize(
                (self.width * self.scale, self.height * self.scale),
                resample=Image.Resampling.NEAREST
            )
        else:
            display_image = self.image
        self._photo = ImageTk.PhotoImage(display_image)
        self.canvas.config(
            width=self.width * self.scale,
            height=self.height * self.scale
        )
        self.canvas.itemconfig(self._image_id, image=self._photo)
        self.root.update()
        self.root.update_idletasks()

    def draw_qr(self, y_offset: int, qr_bits: list, scale: int = 3) -> None:
        """
        This function uses Pillow to render a set of bits as black and white rectangles, such as a QR code.

        :param y_offset: The top margin above the rendered bits
        :param qr_bits: The bits to render, as a list of lists of ones and zeroes
        :param scale: The render scale to make it show up easier on the screen
        :return: Nothing
        """
        self.fill(self.WHITE)
        size = len(qr_bits)
        x_offset = (128 - size * scale) // 2
        for y in range(size):
            for x in range(size):
                if qr_bits[y][x]:
                    starting_x_position = x_offset + x * scale
                    starting_y_position = y_offset + y * scale
                    width = scale
                    height = scale
                    self.draw.rectangle(
                        (starting_x_position, starting_y_position, starting_x_position + width,
                         starting_y_position + height),
                        self.BLACK
                    )
        self._show()
