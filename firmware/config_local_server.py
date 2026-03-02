import http.server
import socketserver
import webbrowser

from config_data import html_form, html_reboot, default_token, DEFAULT_WIFI_NETWORKS
from firmware.config_base import ConfigBase
from firmware.screen_tk import ScreenBase

local_token = default_token()
additional_network = {}
ready = False


class CustomHandler(http.server.SimpleHTTPRequestHandler):

    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self) -> None:
        content = html_form("abc123def456", local_token, additional_network)
        self._set_response()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self) -> None:
        global local_token
        global ready
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
        local_token = d.get("github_token")
        ssid = d.get("wifi_ssid")
        password = d.get("wifi_password")
        if ssid and password:
            additional_network[ssid] = password
        ready = True
        self._set_response(200)
        self.wfile.write(html_reboot().encode('utf-8'))
        return


class ConfigLocalServer(ConfigBase):

    def __init__(self, valid_config: bool = False):
        self.valid_config = valid_config

    def wifi_networks(self) -> list:
        return DEFAULT_WIFI_NETWORKS | additional_network

    def github_token(self) -> str:
        return local_token

    def establish_config(self, screen: ScreenBase = None) -> None:
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
                if ready:
                    return


if __name__ == "__main__":
    c = ConfigLocalServer()
    c.establish_config()
