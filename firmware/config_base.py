from firmware.screen_base import ScreenBase


class ConfigBase:
    """
    This class defines the required configuration management API, which is pretty minimal, but provides
    everything needed to provision a box.
    """

    def wifi_networks(self) -> dict:
        """
        Provides all known Wi-Fi networks, including any defaults and additional entries.

        :return: A dict of Wi-Fi entries, with keys as network names and values as network passwords
        """
        raise NotImplementedError()

    def github_token(self) -> str:
        """
        Provides the user-entered GitHub token, which should have write access to the repo.

        :return: A string GitHub token, like ghp_abc123....
        """
        raise NotImplementedError()

    def establish_config(self, screen: ScreenBase | None = None) -> None:
        """
        Call this at boot to initialize this config class, either by drawing from an existing runtime
        configuration file, or by creating a new one.

        :param screen: If provided, this allows for the configuration class to interact with the user.
        :return: Nothing
        """
        raise NotImplementedError()
