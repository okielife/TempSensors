# noinspection PyPackageRequirements
from ds18x20 import DS18X20
# noinspection PyPackageRequirements
from machine import RTC, WDT, Pin
# noinspection PyPackageRequirements
from network import WLAN, STA_IF
# noinspection PyPackageRequirements
from onewire import OneWire
# noinspection PyPackageRequirements
from ujson import load as load_json
# noinspection PyPackageRequirements
from urequests import get, put

from time import ticks_ms, ticks_diff, localtime, sleep

try:
    from temperature.board_base import BoardBase
except ImportError:
    BoardBase = object


class BoardPico(BoardBase):
    ONE_WIRE_SENSOR_PIN = 28

    # noinspection PyMissingConstructor
    def __init__(self, watchdog_enabled: bool):
        self.watchdog_enabled = watchdog_enabled
        self.wlan = WLAN(STA_IF)
        self.wdt: WDT | None = None
        self.ds18x20: DS18X20 | None = None
        self._led = Pin('LED', Pin.OUT)
        self.pins = {}
        ow = OneWire(Pin(BoardPico.ONE_WIRE_SENSOR_PIN))
        self.ds18x20 = DS18X20(ow)

    def active(self, active: bool) -> None:
        self.wlan.active(active)

    def isconnected(self) -> bool:
        return self.wlan.isconnected()

    def ifconfig(self) -> tuple[str, str, str, str]:
        return self.wlan.ifconfig()

    def config(self, key: str) -> str:
        return self.wlan.config(key)

    def scan(self) -> list[tuple]:
        return self.wlan.scan()

    def connect(self, ssid: str, pw: str) -> None:
        return self.wlan.connect(ssid, pw)

    def http_get(self, url: str):
        return get(url)

    def http_put(self, url: str, headers: dict, json: dict):
        return put(url, headers=headers, json=json)

    # noinspection PyUnusedLocal
    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]):
        RTC().datetime(timestamp)

    def create_watchdog(self, timeout: int):
        if self.watchdog_enabled:
            self.wdt = WDT(timeout=timeout)

    def feed_watchdog(self):
        if self.watchdog_enabled:
            self.wdt.feed()

    def ds18x20_scan(self) -> list[bytes]:
        return self.ds18x20.scan()

    def ds18x20_read_temp(self, rom: bytes):
        return self.ds18x20.read_temp(rom)

    def ds18x20_convert_temp(self):
        self.ds18x20.convert_temp()

    def load_json(self, json_bytes) -> dict:
        return load_json(json_bytes)

    def localtime(self, seconds: int = None):
        if seconds is None:
            return localtime()
        return localtime(seconds)

    def ticks_ms(self) -> int:
        return ticks_ms()

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        return ticks_diff(milliseconds_a, milliseconds_b)

    def system_hang(self, seconds: int = None):
        if seconds is None:
            while True:
                sleep(1)
                self.feed_watchdog()
        else:
            for i in range(seconds):
                sleep(1)
                self.feed_watchdog()

    def sleep(self, seconds: float):
        if seconds > 3:
            for i in range(int(seconds)):
                sleep(1)
                self.feed_watchdog()
        else:
            sleep(seconds)

    def run_forever(self) -> bool:
        return True

    def print(self, message: str):
        print(message)
