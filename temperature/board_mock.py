from time import time

from temperature.board_base import BoardBase, ResponseBase, PinBase


class ResponseMock(ResponseBase):

    # noinspection PyMissingConstructor
    def __init__(self, throw: bool = False):
        if throw:
            raise Exception()
        self.status_code = 200
        self.raw = "\b2010"


class WatchdogMock:
    def feed(self):
        pass


class PinMock(PinBase):
    IN = 0
    OUT = 1
    PULL_UP = 0

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(self, pin_id: int | str, direction: int = IN, pull: int = 0):
        self.pin_id = pin_id
        self.value_on = False

    def on(self) -> None:
        self.value_on = True

    def off(self) -> None:
        self.value_on = False

    def toggle(self) -> None:
        self.value_on = not self.value_on


class BoardMock(BoardBase):

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(
            self, verbose: bool = False,
            throw_rtc: bool = False, throw_http: bool = False, wifi_connect: bool = True,
            ds18x20_missing_entry: bool = False, ds18x20_read_failure: bool = False,
            continue_running_after_first_iteration: bool = False
    ):
        # config flags
        self.verbose = verbose
        self.throw_rtc = throw_rtc
        self.throw_http = throw_http
        self.wifi_connect = wifi_connect
        self.ds18x20_missing_entry = ds18x20_missing_entry
        self.ds18x20_read_failure = ds18x20_read_failure
        self.continue_running_after_first_iteration = continue_running_after_first_iteration
        # state data
        self.activated = False
        self.connected = False
        self.ip = ''
        self.ssid = ''
        self.pw = ''
        self.known_ssids = ["MiFi8000-C1DE", "EmeraldWiFi"]
        self.watchdog = WatchdogMock()
        self.watchdog_watching = False
        self.pins = {}
        self.clock = time() * 1000
        self.printed_messages_for_testing = []

    def led(self) -> PinMock:
        return PinMock('led')

    def active(self, active: bool) -> None:
        self.activated = active

    def isconnected(self) -> bool:
        assert self.activated
        return self.connected

    def ifconfig(self) -> tuple[str, str, str, str]:
        return self.ip, '', '', ''

    def config(self, key: str) -> str:
        assert key == 'ssid'
        return self.ssid

    def scan(self) -> list[tuple[bytes, bytes, int, int, int, int]]:
        return [(x.encode('utf-8'), b"", 0, 0, 2, 0) for x in self.known_ssids]

    def connect(self, ssid: str, pw: str) -> None:
        if not self.wifi_connect:
            return
        # return
        if ssid in self.known_ssids:
            self.connected = True
            self.ssid = ssid
            self.pw = pw
            self.ip = '127.0.0.1'

    def http_get(self, url: str):
        return ResponseMock(self.throw_http)

    def http_put(self, _: str, headers: dict, json: dict):
        return ResponseMock(self.throw_http)

    # noinspection PyUnusedLocal
    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]):
        if self.throw_rtc:
            raise Exception()
        year, month, day, weekday, hours, minutes, seconds, sub_seconds = timestamp
        if self.verbose:  # pragma: no cover
            print(f"RTC clock set to: {year}-{month}-{day} {hours}:{minutes}:{seconds}")

    def create_watchdog(self, timeout: int):
        self.watchdog_watching = True

    def feed_watchdog(self):
        self.watchdog.feed()

    def pin_create(self, pin_id: int | str, direction: int = PinMock.IN, pull: int = PinMock.PULL_UP):
        self.pins[pin_id] = PinMock(pin_id, direction, pull)
        return self.pins[pin_id]

    def set_pin_on(self, pin_id: int | str):
        self.pins[pin_id].on()

    def set_pin_off(self, pin_id: int | str):
        self.pins[pin_id].off()

    def set_pin_toggle(self, pin_id: int | str):
        self.pins[pin_id].toggle()

    def ds18x20_scan(self) -> list[bytes]:
        if self.ds18x20_missing_entry:
            return []
        return [b'(\x93d[\x00\x00\x00\xb4', b'(\xa7\x0fF\xd48h:']

    def ds18x20_read_temp(self, rom: bytes):
        if self.ds18x20_read_failure:
            raise Exception()
        import random
        t = random.randint(-20, 40)
        if self.verbose:  # pragma: no cover
            print(f"Reading temperature as {t} Celsius")
        return t

    def ds18x20_convert_temp(self):
        pass

    def load_json(self, _) -> dict:
        return {
            "sensors": {
                "03": {
                    "hex": "2893645b000000b4",
                    "active": True,
                    "short_name": "Em Garage Fridge",
                },
                "13": {
                    "hex": "28a70f46d438683a",
                    "active": True,
                    "short_name": "Em Garage Freezer",
                },
                "98": {
                    "hex": "someHexCodeHere",
                    "active": False,
                }
            },
            "rom_hex_to_cable_number": {
                "2893645b000000b4": "03",
                "28a70f46d438683a": "13",
                "someHexCodeHere": "98"
            },
        }

    def localtime(self, seconds: int = None):
        return 2025, 1, 19, 10, 55, 29, 1

    def ticks_ms(self) -> int:
        return int(time() * 1000 - self.clock)

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        return 1_000_000  # return something big so it always advances

    def system_hang(self, seconds: int = None):
        if seconds is None:
            raise RuntimeError("Mocking the sensor box infinite system hang with an exception")
        # if there was a short positive hang, then it just returns

    def sleep(self, seconds: float):
        return

    def run_forever(self) -> bool:
        return self.continue_running_after_first_iteration

    def print(self, message: str):
        self.printed_messages_for_testing.append(message)
