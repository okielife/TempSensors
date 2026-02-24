from unittest import TestCase

from temperature.board_base import BoardBase, ResponseBase, PinBase

# This file is really just a test of the API.
# I will assert that it raises NotImplementedError
# If something is wrong with the signature/call, then it will give a TypeError

class TestResponseBase(TestCase):
    def test_response_api(self):
        r = ResponseBase()
        self.assertIsInstance(r.status_code, int)
        self.assertIsInstance(r.text, str)
        self.assertIsInstance(r.raw, bytes)
        with self.assertRaises(NotImplementedError):
            r.close()


class TestPinBase(TestCase):
    def test_pin_api(self):
        p = PinBase(0, 0, 0)
        with self.assertRaises(NotImplementedError):
            p.on()
        with self.assertRaises(NotImplementedError):
            p.off()
        with self.assertRaises(NotImplementedError):
            p.toggle()
        with self.assertRaises(NotImplementedError):
            p.value()


class TestBoardBase(TestCase):
    def test_board_api(self):
        b = BoardBase()
        with self.assertRaises(NotImplementedError):
            b.active(True)
        with self.assertRaises(NotImplementedError):
            b.isconnected()
        with self.assertRaises(NotImplementedError):
            b.ifconfig()
        with self.assertRaises(NotImplementedError):
            b.config("")
        with self.assertRaises(NotImplementedError):
            b.scan()
        with self.assertRaises(NotImplementedError):
            b.connect("netowrk", "password")
        with self.assertRaises(NotImplementedError):
            b.http_get("https://url")
        with self.assertRaises(NotImplementedError):
            b.http_put("url", {'header': 'value'}, {'data': 'value'})
        with self.assertRaises(NotImplementedError):
            b.rtc_datetime((2020, 1, 21, 2, 10, 32, 36, 0))
        with self.assertRaises(NotImplementedError):
            b.create_watchdog(8000)
        with self.assertRaises(NotImplementedError):
            b.feed_watchdog()
        with self.assertRaises(NotImplementedError):
            b.ds18x20_scan()
        with self.assertRaises(NotImplementedError):
            b.ds18x20_read_temp(b'')
        with self.assertRaises(NotImplementedError):
            b.ds18x20_convert_temp()
        with self.assertRaises(NotImplementedError):
            b.load_json(b'{}')
        with self.assertRaises(NotImplementedError):
            b.localtime(0)
        with self.assertRaises(NotImplementedError):
            b.ticks_ms()
        with self.assertRaises(NotImplementedError):
            b.ticks_diff(1, 2)
        with self.assertRaises(NotImplementedError):
            b.system_hang(0)
        with self.assertRaises(NotImplementedError):
            b.sleep(1)
        with self.assertRaises(NotImplementedError):
            b.run_forever()
        with self.assertRaises(NotImplementedError):
            b.print("message")
