from random import randint
from time import time
from typing import Any

from firmware.board_base import BoardBase, ResponseBase, PinBase


class ResponseMock(ResponseBase):

    # noinspection PyMissingConstructor
    def __init__(self, throw: bool = False, bad_status: bool = False) -> None:
        if throw:
            raise Exception()
        self.status_code = 400 if bad_status else 200
        self.text = ""
        self.raw = b""

    def close(self) -> None:
        return


class PinMock(PinBase):
    IN = 0
    OUT = 1
    PULL_UP = 0

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(self, pin_id, direction: int = IN, pull: int = 0):
        self.pin_id = pin_id
        self.value_on = False

    def on(self) -> None:
        self.value_on = True

    def off(self) -> None:
        self.value_on = False

    def toggle(self) -> None:
        self.value_on = not self.value_on

    def value(self) -> int:
        return 1 if self.value_on else 0


class BoardMock(BoardBase):

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(
            self,
            watchdog_enabled: bool,  # TODO: I think make this default ON
            verbose: bool = False,
            throw_rtc: bool = False,
            throw_http: bool = False,
            bad_http_get_status: bool = False,
            bad_http_put_status: bool = False,
            wifi_connect: bool = True,
            ds18x20_read_failure: bool = False,
            continue_running_after_first_iteration: bool = False,
            fixed_temperature_c: float = 1000,
            convert_temp_failure: bool = False,
            bad_ntp_timestamp: bool = False,
            label_missing_from_rom_hex_map: bool = False,
            label_missing_from_sensors: bool = False
    ):
        # config flags
        self.watchdog_enabled = watchdog_enabled
        self.verbose = verbose
        self.throw_rtc = throw_rtc
        self.throw_http = throw_http
        self.bad_http_get_status = bad_http_get_status
        self.bad_http_put_status = bad_http_put_status
        self.wifi_connect = wifi_connect
        self.ds18x20_read_failure = ds18x20_read_failure
        self.continue_running_after_first_iteration = continue_running_after_first_iteration
        self.fixed_temperature_c = fixed_temperature_c
        self.convert_temp_failure = convert_temp_failure
        self.bad_ntp_timestamp = bad_ntp_timestamp
        self.label_missing_from_rom_hex_map = label_missing_from_rom_hex_map
        self.label_missing_from_sensors = label_missing_from_sensors
        # state data
        self.activated = False
        self.connected = False
        self.ip = ''
        self.ssid = ''
        self.pw = ''
        self.known_ssids = ["MiFi8000-C1DE", "EmeraldWiFi"]
        self.watchdog = type("NoopWatchdog", (), {"feed": lambda _: None})()
        self.watchdog_watching = False
        self.pins: dict = {}
        self.clock = time() * 1000
        self.printed_messages_for_testing = ""
        self.found_ds18x20_roms = [b'(\x93d[\x00\x00\x00\xb4', b'(\xa7\x0fF\xd48h:']

    def developer_mode(self) -> bool:
        return not self.watchdog_enabled

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
            self.connected = False
            return
        # return
        if ssid in self.known_ssids:
            self.connected = True
            self.ssid = ssid
            self.pw = pw
            self.ip = '127.0.0.1'

    def http_get(self, url: str) -> ResponseBase:
        return ResponseMock(self.throw_http, self.bad_http_get_status)

    def http_put(self, _: str, headers: dict, json: dict) -> ResponseBase:
        return ResponseMock(self.throw_http, self.bad_http_put_status)

    # noinspection PyUnusedLocal
    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]) -> None:
        if self.throw_rtc:
            raise OSError()
        year, month, day, weekday, hours, minutes, seconds, sub_seconds = timestamp
        if self.verbose:  # pragma: no cover
            print(f"RTC clock set to: {year}-{month}-{day} {hours}:{minutes}:{seconds}")

    def get_ntp_timestamp(self) -> int | None:
        if self.bad_ntp_timestamp:
            return None
        return 1772668800  # roughly March 4, 2026

    def create_watchdog(self, timeout: int) -> None:
        self.watchdog_watching = self.watchdog_enabled

    def feed_watchdog(self) -> None:
        self.watchdog.feed()

    def ds18x20_scan(self) -> list[bytes]:
        return self.found_ds18x20_roms

    def ds18x20_read_temp(self, rom: bytes) -> float:
        if self.ds18x20_read_failure:
            raise OSError()
        if self.fixed_temperature_c != 1000:
            return self.fixed_temperature_c
        t = randint(-20, 40)
        if self.verbose:  # pragma: no cover
            print(f"Reading temperature as {t} Celsius")
        return t

    def ds18x20_convert_temp(self) -> None:
        if self.convert_temp_failure:
            raise Exception("Could not convert temperature")

    def load_json(self, _) -> dict:
        base_data: dict[str, Any] = {
            "sensors": {
                "03": {
                    "hex": "2893645b000000b4",
                    "active": False,
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
        if self.label_missing_from_rom_hex_map:
            base_data["rom_hex_to_cable_number"].pop("2893645b000000b4")
        if self.label_missing_from_sensors:
            base_data["sensors"].pop("03")
        return base_data

    def localtime(self, seconds: int | None = None) -> tuple:
        return 2025, 1, 19, 10, 55, 29, 1

    def ticks_ms(self) -> int:
        return int(time() * 1000 - self.clock)

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        return 1_000_000  # return something big so it always advances

    def system_hang(self, seconds: int | None = None) -> None:
        if seconds is None:
            raise RuntimeError("Mocking the sensor box infinite system hang with an exception")
        # if there was a short positive hang, then it just returns

    def sleep(self, seconds: float) -> None:
        return

    def run_forever(self) -> bool:
        return self.continue_running_after_first_iteration

    def print(self, message: str) -> None:
        self.printed_messages_for_testing += message
