from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

from firmware.font import FONT
from firmware.screen_base import ScreenBase


def rgb_to_565(r: int, g: int, b: int) -> int:
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
    BLACK = rgb_to_565(0, 0, 0)
    WHITE = rgb_to_565(255, 255, 255)
    RED = rgb_to_565(255, 0, 0)
    GREEN = rgb_to_565(0, 255, 0)
    BLUE = rgb_to_565(0, 0, 255)
    YELLOW = rgb_to_565(255, 255, 0)
    GRAY = rgb_to_565(128, 128, 128)

    # noinspection PyUnusedLocal,PyPep8Naming,PyMissingConstructor
    def __init__(self):

        self.closed = False
        self.width, self.height = 128, 160
        self.scale = 2  # 1 = real size, 2 = double, etc.

        self.image = Image.new("RGB", (128, 160), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

        self.root = tk.Tk()
        self.root.title("TFT Emulator")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height
        )
        self.canvas.pack()

        self._photo = ImageTk.PhotoImage(self.image)
        self._image_id = self.canvas.create_image(
            0, 0, anchor="nw", image=self._photo
        )

        self.show()

    def _on_close(self) -> None:
        self.closed = True
        self.root.destroy()

    def fill(self, color: int) -> None:
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)
        self.show()

    def circle(self, point: tuple, radius: int, color: int) -> None:
        x_center, y_center = point
        x_min, x_max = x_center - radius, x_center + radius
        y_min, y_max = y_center - radius, y_center + radius
        c = _color565_to_rgb(color)
        self.draw.ellipse((x_min, y_min, x_max, y_max), outline=c)

    def text(self, point: tuple, text: str, color: int, size: int = 1, nowrap: bool = True) -> None:

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

        self.show()

    def rect(self, p1: tuple, p2: tuple, color: int) -> None:
        c = _color565_to_rgb(color)
        self.draw.rectangle((p1, p2), outline=c)
        self.show()

    def fillrect(self, point: tuple, size: tuple, color: int) -> None:
        x, y = point
        w, h = size
        c = _color565_to_rgb(color)
        self.draw.rectangle((x, y, x + w, y + h), fill=c)
        self.show()

    def hline(self, point: tuple, length: int, color: int) -> None:
        x, y = point
        c = _color565_to_rgb(color)
        self.draw.line((x, y, x + length, y), fill=c)
        self.show()

    def vline(self, point: tuple, length: int, color: int) -> None:
        x, y = point
        c = _color565_to_rgb(color)
        self.draw.line((x, y, x, y + length), fill=c)
        self.show()

    def show(self) -> None:
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
        self.show()
