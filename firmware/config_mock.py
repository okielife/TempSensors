from firmware.config_base import ConfigBase
from firmware.config_data import DEFAULT_WIFI_NETWORKS, default_token
from firmware.screen_base import ScreenBase


class ConfigMock(ConfigBase):
    """
    This class implements the configuration management API, specifically for unit testing workflows.
    This class utilizes defaults and has no actual provisioning functionality.
    """

    def __init__(self) -> None:
        """
        Constructs a mock configuration class, storing defaults as class members
        """
        self.networks = DEFAULT_WIFI_NETWORKS
        self.token = default_token()

    def wifi_networks(self) -> dict:
        """
        Returns the default Wi-Fi network information

        :return: A dict of network information, with keys as SSID and values as PW.
        """
        return self.networks

    def github_token(self) -> str:
        """
        Returns the default GitHub token

        :return: A string token
        """
        return self.token

    def establish_config(self, screen: ScreenBase | None = None) -> None:
        """
        In this mock class, this function does nothing.

        :param screen: Not used for this mock class
        :return: Nothing
        """
        return
