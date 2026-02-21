from unittest import TestCase

from temperature.config_template import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN


class TestConfig(TestCase):
    def test_config_types(self):
        self.assertIsInstance(WIFI_NETWORKS, list)
        for wifi_network in WIFI_NETWORKS:
            self.assertIsInstance(wifi_network, tuple)
            self.assertEqual(len(wifi_network), 2)
        self.assertIsInstance(CONNECTED_SENSORS, list)
        for sensor in CONNECTED_SENSORS:
            self.assertIsInstance(sensor, tuple)
            self.assertEqual(len(sensor), 2)
        self.assertIsInstance(GITHUB_TOKEN, str)
