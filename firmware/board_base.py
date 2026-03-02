class ResponseBase:
    def __init__(self):
        self.status_code = 0
        self.text = ""
        self.raw = b""

    def close(self) -> None:
        raise NotImplementedError


class PinBase:

    # noinspection PyUnusedLocal
    def __init__(self, pin_id, direction: int = 0, pull: int = 0):
        pass

    def on(self) -> None:
        raise NotImplementedError

    def off(self) -> None:
        raise NotImplementedError

    def toggle(self) -> None:
        raise NotImplementedError

    def value(self) -> int:
        raise NotImplementedError


class BoardBase:

    # noinspection PyUnusedLocal
    def __init__(self):
        self.printed_messages_for_testing: list[str] = []

    def developer_mode(self) -> bool:
        raise NotImplementedError

    def active(self, active: bool) -> None:
        raise NotImplementedError

    def isconnected(self) -> bool:
        raise NotImplementedError

    def ifconfig(self) -> tuple[str, str, str, str]:
        raise NotImplementedError

    def config(self, key: str) -> str:
        raise NotImplementedError

    def scan(self) -> list[tuple[bytes, bytes, int, int, int, int]]:
        raise NotImplementedError

    def connect(self, ssid: str, pw: str) -> None:
        raise NotImplementedError

    def http_get(self, url: str) -> ResponseBase:
        raise NotImplementedError

    def http_put(self, _: str, headers: dict, json: dict) -> ResponseBase:
        raise NotImplementedError

    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]) -> None:
        raise NotImplementedError

    def create_watchdog(self, timeout: int) -> None:
        raise NotImplementedError

    def feed_watchdog(self) -> None:
        raise NotImplementedError

    def ds18x20_scan(self) -> list[bytes]:
        raise NotImplementedError

    def ds18x20_read_temp(self, rom: bytes) -> float:
        raise NotImplementedError

    def ds18x20_convert_temp(self) -> None:
        raise NotImplementedError

    def load_json(self, json_bytes) -> dict:
        raise NotImplementedError

    def localtime(self, seconds: int = None) -> tuple:
        raise NotImplementedError

    def ticks_ms(self) -> int:
        raise NotImplementedError

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        raise NotImplementedError

    def system_hang(self, seconds: int = None) -> None:
        raise NotImplementedError

    def sleep(self, seconds: float) -> None:
        raise NotImplementedError

    def run_forever(self) -> bool:
        raise NotImplementedError

    def print(self, message: str) -> None:
        raise NotImplementedError
