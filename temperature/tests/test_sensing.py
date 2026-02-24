from unittest import TestCase

from temperature.board_mock import BoardMock
from temperature.screen_mock import ScreenMock
from temperature.sensing import SensorBox


class TestSensing(TestCase):

    def setUp(self):
        self.screen = ScreenMock()
        self.board = BoardMock()

    def test_construction(self):
        """Given the inputs we have set up to mock, we would expect it to be connected and set up"""
        s = SensorBox(self.screen, self.board)
        self.assertTrue(len(s.sensors) == 2)
        self.assertTrue(s.board.isconnected())
        self.assertTrue(s.time_synced)
        s.run()

    def test_missing_sensor_reports_fatal(self):
        self.board.ds18x20_missing_entry = True
        with self.assertRaises(Exception):
            SensorBox(self.screen, self.board)

    def test_clock_sync_reports_error_but_continues(self):
        self.board.throw_rtc = True
        s = SensorBox(self.screen, self.board)
        self.assertTrue(any("SYNC" in s for s in s.board.printed_messages_for_testing))

    def test_sensor_config_reports_error_but_continues(self):
        self.board.throw_http = True
        s = SensorBox(self.screen, self.board)
        self.assertTrue(any("sensor config" in s for s in s.board.printed_messages_for_testing))

    def test_wifi_disconnected_reports_error_but_continues(self):
        self.board.wifi_connect = False
        s = SensorBox(self.screen, self.board)
        self.assertTrue(any("CHECK" in s for s in s.screen.displayed_messages_for_testing))
        s.run()
        self.assertTrue(any("DISCONNECTED" in s for s in s.screen.displayed_messages_for_testing))

    def test_normal_run(self):
        s = SensorBox(self.screen, self.board)
        s.run()

    def test_tries_to_run_without_wifi(self):
        self.board.wifi_connect = False
        s = SensorBox(self.screen, self.board)
        s.run()

    def test_tries_to_run_with_sensor_read_failure(self):
        self.board.ds18x20_read_failure = True
        s = SensorBox(self.screen, self.board)
        s.run()

    def test_dev_mode_works(self):
        s = SensorBox(self.screen, self.board)
        s.display_dev_mode_warning()
        self.assertTrue(any("developer mode" in s for s in s.board.printed_messages_for_testing))

    def test_flashing_led(self):
        s = SensorBox(self.screen, self.board)
        s.flash_led(1)
