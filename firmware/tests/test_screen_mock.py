from unittest import TestCase

from firmware.screen_mock import ScreenMock


class TestScreenMock(TestCase):
    def test_api(self):
        s = ScreenMock()
        self.assertFalse(s.displayed_messages_for_testing)
        s.fill(0)
        s.circle((), 0, 0)
        s.text((), "", 0, 0, True)
        s.rect((), (), 0)
        s.fillrect((), (), 0)
        s.hline((), 0, 0)
        s.vline((), 0, 0)
        s.draw_qr(0, [])
