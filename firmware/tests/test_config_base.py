from unittest import TestCase

from firmware.config_base import ConfigBase


class TestConfigBase(TestCase):
    def test_api(self) -> None:
        c = ConfigBase()
        with self.assertRaises(NotImplementedError):
            c.wifi_networks()
        with self.assertRaises(NotImplementedError):
            c.github_token()
        with self.assertRaises(NotImplementedError):
            c.establish_config()
