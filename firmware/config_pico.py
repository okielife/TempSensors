from gc import collect
from json import dump, loads
from os import remove
from socket import getaddrinfo, socket
from time import sleep
from ubinascii import hexlify

# noinspection PyPackageRequirements
from machine import unique_id, reset, Pin
# noinspection PyPackageRequirements
from network import WLAN, AP_IF

from firmware.config_base import ConfigBase
from firmware.config_data import html_form, html_reboot, QR_CODE_192_168_4_1, DEFAULT_WIFI_NETWORKS
from firmware.screen_tft import ScreenTFT, ScreenBase


class ConfigPico(ConfigBase):
    """
    This class implements the configuration management API, specifically for actual hardware usage.
    This class is expected to operate on the hardware, executed via MicroPython.
    During provisioning, an actual Wi-Fi access point and HTTP server is established to provide user functionality.
    """

    #: The board Pin connected to a switch (and to GND) used to detect factory reset mode
    PIN_FACTORY_RESET = 6

    _CONFIG_FILE = "config.json"

    def __init__(self) -> None:
        """
        Constructs a new configuration management instance. For this hardware version, this involves retrieving the
        actual unique ID for the board, reading the factory reset Pin state, and establishing member variables.
        """
        self.device_id = hexlify(unique_id()).decode()
        self.device_id_short = self.device_id[0:4]
        self.ap_wifi_name = f"Sensor_{self.device_id_short}"
        self.token = ""
        self.additional_wifi_network: dict = {}
        self.ready_to_reset = False
        factory_reset_pin = Pin(ConfigPico.PIN_FACTORY_RESET, Pin.IN, Pin.PULL_UP)
        perform_factory_reset = (factory_reset_pin.value() == 0)
        if perform_factory_reset:
            print("**Factory reset pin active, deleting previous configuration**")
            # noinspection PyBroadException
            try:
                remove(ConfigPico._CONFIG_FILE)
            except Exception:  # it's fine if it didn't exist or anything
                pass

    def wifi_networks(self) -> dict:
        """
        Returns a merge of the default known Wi-Fi networks, along with the optional user-provided extra network.

        :return: A dict of network information, with keys as SSID and values as PW.
        """
        return DEFAULT_WIFI_NETWORKS | self.additional_wifi_network

    def github_token(self) -> str:
        """
        Returns the user-provided GitHub token

        :return: A string token
        """
        return self.token

    def _valid_config_found(self) -> bool:
        # noinspection PyBroadException
        try:
            with open(ConfigPico._CONFIG_FILE) as f:
                contents = f.read()
            config = loads(contents)
            self.additional_wifi_network = config['additional_wifi_network']
            self.token = config['github_token']
            return True
        except Exception:
            return False

    def _handle_get(self, conn) -> None:
        html = html_form(self.device_id, self.token, self.additional_wifi_network)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}"
        ).format(len(html), html)
        conn.sendall(response)

    def _get_config(self) -> dict:
        return {
            "additional_wifi_network": self.additional_wifi_network,
            "github_token": self.token,
        }

    def _handle_post(self, _, request) -> None:
        body = request.split("\r\n\r\n", 1)[1]
        form = {}
        pairs = body.split("&")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                value = value.replace("+", " ")
                form[key] = value
        extra_wifi_ssid = form.get("wifi_ssid", "")
        extra_wifi_password = form.get("wifi_password", "")
        self.token = form.get("github_token", "")
        self.additional_wifi_network = {}
        if extra_wifi_ssid and extra_wifi_password:
            self.additional_wifi_network["wifi_ssid"] = extra_wifi_ssid
        with open(ConfigPico._CONFIG_FILE, "w") as f:
            dump(self._get_config(), f)
        self.ready_to_reset = True

    def establish_config(self, screen: ScreenBase = None) -> None:
        """
        If a valid configuration is already available on the device, this function returns without any action.
        To create a new configuration, this function will establish a Wi-Fi access point and an HTTP server.
        This device will also present the user with information including a QR code on the screen to ease
        the provisioning process.  Once the user has submitted the information, the data is saved, and the
        board is reset.

        :param screen: An optional display to present information the user.  It will be in the terminal, also.
        :return: Nothing
        """
        if self._valid_config_found():
            print(f"Valid configuration found:\n{self._get_config()}\nAll done.")
            return
        collect()
        print("No valid configuration found, entering provisioning mode.")
        ap = WLAN(AP_IF)
        ap.active(False)
        sleep(1)
        ap.active(True)
        ap.config(essid=self.ap_wifi_name, security=0)
        print(f"Provisioning mode. Connect to Wi-Fi: {self.ap_wifi_name}")
        print("Then browse to http://192.168.4.1")
        if screen:
            screen.text((1, 0), "Setup Mode", screen.WHITE, 2)
            screen.text((1, 20), "Connect to Wi-Fi:", screen.WHITE, 1)
            screen.text((20, 30), f"{self.ap_wifi_name}", screen.WHITE, 1)
            screen.text((1, 42), "Go http://192.168.4.1", screen.WHITE, 1)
            screen.text((1, 52), "Or scan to continue:", screen.WHITE, 1)
            screen.draw_qr(65, QR_CODE_192_168_4_1)
        addr = getaddrinfo("0.0.0.0", 80)[0][-1]
        sock = socket()
        sock.bind(addr)
        sock.listen(1)
        while True:
            conn, addr = sock.accept()
            request = conn.recv(2048).decode()
            if "GET /" in request:
                self._handle_get(conn)
            elif "POST /" in request:
                self._handle_post(conn, request)
            if not self.ready_to_reset:
                # just close the current connection and continue
                conn.close()
            else:
                message = html_reboot()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    "Connection: close\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}"
                ).format(len(message), message)
                conn.sendall(response)
                conn.close()
                sock.close()
                sleep(1)  # give TCP stack time to flush
                reset()


if __name__ == "__main__":
    c = ConfigPico()
    s = ScreenTFT()
    c.establish_config(s)
