from unittest import TestCase

from temperature.tests.mock import SPI, TFT, DS18X20, RTC, Response, set_actually_sleep, WLAN
from temperature.sensing import OperatingMode, SensorBox


class TestSensing(TestCase):

    def setUp(self):
        set_actually_sleep(False)

    def tearDown(self):
        set_actually_sleep(True)

    def test_construction(self):
        """Given the inputs we have set up to mock, we would expect it to be connected and set up"""
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        self.assertTrue(len(s.sensors) == 2)
        self.assertTrue(s.wlan.isconnected())
        self.assertTrue(s.time_synced)
        # s.run() this will hang on CI

    def test_spi_failure_reports_on_screen_failure(self):
        SPI.__throw__ = True
        with self.assertRaises(Exception):
            SensorBox(operating_mode=OperatingMode.UnitTesting)
        SPI.__throw__ = False

    def test_missing_sensor_reports_fatal(self):
        DS18X20.__missing_entry__ = True
        with self.assertRaises(Exception):
            SensorBox(operating_mode=OperatingMode.UnitTesting)
        self.assertIn("Could not initialize sensor", TFT.LatestText)
        DS18X20.__missing_entry__ = False

    def test_clock_sync_reports_error_but_continues(self):
        RTC.__throw__ = True
        SensorBox(operating_mode=OperatingMode.UnitTesting)
        self.assertIn("SYNC", TFT.LatestText)
        RTC.__throw__ = False

    def test_sensor_config_reports_error_but_continues(self):
        Response.__throw__ = True
        SensorBox(operating_mode=OperatingMode.UnitTesting)
        self.assertIn("sensor config", TFT.LatestText)
        Response.__throw__ = False

    def test_wifi_disconnected_reports_error_but_continues(self):
        WLAN.__connected__ = False
        SensorBox(operating_mode=OperatingMode.UnitTesting)
        self.assertIn("CHECK", TFT.LatestText)
        WLAN.__connected__ = True

    def test_normal_run(self):
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        s.run()

    def test_tries_to_run_without_wifi(self):
        WLAN.__connected__ = False
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        s.run()
        WLAN.__connected__ = True

    def test_tries_to_run_with_sensor_read_failure(self):
        DS18X20.__read_failure__ = False
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        s.run()
        DS18X20.__read_failure__ = True

    def test_dev_mode_works(self):
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        s.display_dev_mode_warning()
        self.assertIn("DEV MODE", TFT.LatestText)

    def test_flashing_led(self):
        s = SensorBox(operating_mode=OperatingMode.UnitTesting)
        s.flash_led(1)
