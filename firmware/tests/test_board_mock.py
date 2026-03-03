from unittest import TestCase

from firmware.board_mock import ResponseMock, PinMock, BoardMock


class TestResponseMock(TestCase):
    def test_response_api(self):
        r = ResponseMock()
        self.assertIsInstance(r.status_code, int)
        self.assertIsInstance(r.text, str)
        self.assertIsInstance(r.raw, bytes)
        r.close()


class TestPinMock(TestCase):
    def test_pin_api(self):
        p = PinMock(0, 0, 0)
        p.on()
        self.assertEqual(1, p.value())
        p.off()
        self.assertEqual(0, p.value())
        p.toggle()
        self.assertEqual(1, p.value())


class TestBoardMock(TestCase):
    def test_system_hang(self):
        b = BoardMock(watchdog_enabled=False)
        b.system_hang(1)  # should pass fine
        with self.assertRaises(Exception):
            b.system_hang()
