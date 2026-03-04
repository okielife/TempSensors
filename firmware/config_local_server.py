import http.server
import socketserver
import webbrowser

from firmware.config_data import html_form, html_reboot, default_token, DEFAULT_WIFI_NETWORKS
from firmware.config_base import ConfigBase
from firmware.screen_tk import ScreenBase

_local_token: str = default_token()
_additional_network: dict = {}
_ready: bool = False


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """
    This class is a custom, and very simple, HTTP handler for the GET and POST provisioning steps.
    """

    def _set_response(self, status_code: int = 200) -> None:
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self) -> None:
        """
        This method handles the GET calls by encoding HTML content in a response object

        :return: Nothing
        """
        content = html_form("abc123def456", _local_token, _additional_network)
        self._set_response()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self) -> None:
        """
        This method handles the POST calls by parsing user data, storing it, setting the ready flag,
        and finally encoding an HTML completion message in a response object.

        :return: Nothing
        """
        global _local_token
        global _ready
        content_length = int(self.headers['Content-Length'])
        post_data_bytes = self.rfile.read(content_length)
        post_data_str = post_data_bytes.decode('utf-8')
        d = {}
        pairs = post_data_str.split("&")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                value = value.replace("+", " ")
                d[key] = value
        _local_token = d.get("github_token", "")
        ssid = d.get("wifi_ssid", "")
        password = d.get("wifi_password", "")
        if ssid and password:
            _additional_network[ssid] = password
        _ready = True
        self._set_response(200)
        self.wfile.write(html_reboot().encode('utf-8'))
        return


class ConfigLocalServer(ConfigBase):
    """
    This class implements the configuration management API, specifically for local development workflows.
    In this class, a local server is established, in Python, and a landing page opens to complete provisioning,
    right on the developer machine.
    """

    def __init__(self, valid_config: bool = False) -> None:
        """
        Constructs a configuration manager instance.

        :param valid_config: If True, this indicates provisioning is already complete and this class does nothing.
        """
        self.valid_config = valid_config

    def wifi_networks(self) -> dict:
        """
        Returns a merge of the default known Wi-Fi networks, along with the optional user-provided extra network.

        :return: A dict of network information, with keys as SSID and values as PW.
        """
        return DEFAULT_WIFI_NETWORKS | _additional_network

    def github_token(self) -> str:
        """
        Returns the user-provided GitHub token

        :return: A string token
        """
        return _local_token

    def establish_config(self, screen: ScreenBase | None = None) -> None:
        """
        When this configuration management class is executed, it spins up a local server to mimic
        device provisioning.  The behavior mimics the real hardware behavior very closely.

        :param screen: An optional screen - if utilized, it will offer additional details to the user.
        :return: Nothing
        """
        port = 5000
        if self.valid_config:
            return
        if screen:
            screen.text((1, 0), "Setup Mode", screen.WHITE, 2)
            screen.text((1, 20), "Browse to:", screen.WHITE, 1)
            screen.text((1, 30), f"http://127.0.0.1:{port}", screen.WHITE, 1)
            webbrowser.open(f"http://127.0.0.1:{port}")
        socketserver.TCPServer.allow_reuse_address = True
        # noinspection PyTypeChecker
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"Serving at port {port} with a custom handler")
            while True:  # Example: Handles 5 requests then stops
                httpd.handle_request()  # Processes one request and returns
                if _ready:
                    return


if __name__ == "__main__":
    c = ConfigLocalServer()
    c.establish_config()
