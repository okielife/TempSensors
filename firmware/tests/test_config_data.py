from unittest import TestCase

from firmware.config_data import DEFAULT_WIFI_NETWORKS, QR_CODE_192_168_4_1, html_form, html_reboot, default_token


class TestConfigData(TestCase):
    def test_api(self):
        self.assertIsInstance(DEFAULT_WIFI_NETWORKS, dict)
        self.assertIsInstance(QR_CODE_192_168_4_1, list)
        self.assertIsInstance(html_form("id", "token", {'ssid': 'pw'}), str)
        self.assertIsInstance(html_reboot(), str)
        self.assertIsInstance(default_token(), str)
