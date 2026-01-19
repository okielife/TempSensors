from unittest import TestCase

from temperature.sensing import SensorBox


class TestSensing(TestCase):
    def test_construction(self):
        """Given the inputs we have set up to mock, we would expect it to be connected and set up"""
        s = SensorBox(enable_watchdog=False)
        self.assertTrue(len(s.sensors) == 2)
        self.assertTrue(s.wlan.isconnected())
        self.assertTrue(s.time_synced)
