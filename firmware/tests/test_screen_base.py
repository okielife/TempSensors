from unittest import TestCase

from firmware.screen_base import ScreenBase

# This file is really just a test of the API.
# I will assert that it raises NotImplementedError
# If something is wrong with the signature/call, then it will give a TypeError


class TestScreenBase(TestCase):
    def test_screen_api(self):
        s = ScreenBase()
        p1 = (0, 0)
        p2 = (1, 1)
        color = ScreenBase.BLACK
        radius = 1
        length = 1
        text = "Hello"
        size = (128, 160)
        self.assertIsInstance(s.displayed_messages_for_testing, list)
        with self.assertRaises(NotImplementedError):
            s.fill(color)
        with self.assertRaises(NotImplementedError):
            s.circle(p1, radius, color)
        with self.assertRaises(NotImplementedError):
            s.text(p1, text, color, size=1, nowrap=True)
        with self.assertRaises(NotImplementedError):
            s.rect(p1, p2, color)
        with self.assertRaises(NotImplementedError):
            s.fillrect(p1, size, color)
        with self.assertRaises(NotImplementedError):
            s.hline(p1, length, color)
        with self.assertRaises(NotImplementedError):
            s.vline(p1, length, color)
