from firmware.config_base import ConfigBase
from firmware.config_data import DEFAULT_WIFI_NETWORKS, default_token
from firmware.screen_base import ScreenBase


class ConfigMock(ConfigBase):
    def __init__(self):
        self.networks = DEFAULT_WIFI_NETWORKS
        self.token = default_token()

    def wifi_networks(self) -> tuple:
        return self.networks

    def github_token(self) -> str:
        return self.token

    def establish_config(self, _: ScreenBase = None) -> None:
        return
