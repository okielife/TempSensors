from firmware.screen_base import ScreenBase


class ConfigBase:

    def wifi_networks(self) -> dict:
        raise NotImplementedError()

    def github_token(self) -> str:
        raise NotImplementedError()

    def establish_config(self, screen: ScreenBase | None = None) -> None:
        raise NotImplementedError()
