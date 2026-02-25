from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

from firmware.font import FONT
from firmware.screen_base import ScreenBase


class ScreenTk(ScreenBase):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)

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

    def _on_close(self):
        self.closed = True
        self.root.destroy()

    def initr(self):
        pass

    def rgb(self, _):
        pass

    def fill(self, color):
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)
        self.show()

    def circle(self, point, radius, color):
        x_center, y_center = point
        x_min, x_max = x_center - radius, x_center + radius
        y_min, y_max = y_center - radius, y_center + radius
        self.draw.ellipse((x_min, y_min, x_max, y_max), outline=color)

    def text(self, point, text, color, size=1, nowrap=True):

        x, y = point
        cw = FONT["Width"]
        ch = FONT["Height"]
        data = FONT["Data"]
        start = FONT["Start"]

        for ch_i in text:
            code = ord(ch_i)

            if code < start or code > FONT["End"]:
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
                            fill=color
                        )

            x += cw * size + size  # inter-character spacing

            if not nowrap and x >= self.width:
                x = point[0]
                y += ch * size + size

        self.show()

    def rect(self, p1, p2, color):
        self.draw.rectangle((p1, p2), outline=color)
        self.show()

    def fillrect(self, point, size, color):
        x, y = point
        w, h = size
        self.draw.rectangle((x, y, x + w, y + h), fill=color)
        self.show()

    def hline(self, point, length, color):
        x, y = point
        self.draw.line((x, y, x + length, y), fill=color)
        self.show()

    def vline(self, point, length, color):
        x, y = point
        self.draw.line((x, y, x, y + length), fill=color)
        self.show()

    def show(self):
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
