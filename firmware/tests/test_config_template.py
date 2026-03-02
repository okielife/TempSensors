from unittest import TestCase

from firmware.config_template import WIFI_NETWORKS, GITHUB_TOKEN


class TestConfig(TestCase):
    def test_config_types(self):
        self.assertIsInstance(WIFI_NETWORKS, list)
        for wifi_network in WIFI_NETWORKS:
            self.assertIsInstance(wifi_network, tuple)
            self.assertEqual(len(wifi_network), 2)
        self.assertIsInstance(GITHUB_TOKEN, str)
