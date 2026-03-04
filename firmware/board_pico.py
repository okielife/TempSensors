from socket import getaddrinfo, socket, AF_INET, SOCK_DGRAM
from struct import unpack

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

try:
    from time import ticks_ms, ticks_diff, localtime, sleep
except ImportError:  # pragma: only needed when parsing this file with sphinx
    ticks_ms = None
    ticks_diff = None
    localtime = None
    sleep = None

from firmware.board_base import BoardBase


class BoardPico(BoardBase):
    ONE_WIRE_SENSOR_PIN = 28
    DEV_MODE_PIN = 14  # when developing, jump pin GP14 over to GND

    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        dev_pin = Pin(BoardPico.DEV_MODE_PIN, Pin.IN, Pin.PULL_UP)
        self.watchdog_enabled = (dev_pin.value() == 1)
        self.wlan = WLAN(STA_IF)
        self.wdt = None
        self._led = Pin('LED', Pin.OUT)
        self.pins = {}
        ow = OneWire(Pin(BoardPico.ONE_WIRE_SENSOR_PIN))
        self.ds18x20 = DS18X20(ow)

    def developer_mode(self) -> bool:
        return not self.watchdog_enabled

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

    def get_ntp_timestamp(self) -> int | None:
        s = socket(AF_INET, SOCK_DGRAM)
        # noinspection PyBroadException
        try:
            addr = getaddrinfo("pool.ntp.org", 123)[0][-1]
            s.settimeout(5)
            s.sendto(b'\x1b' + 47 * b'\0', addr)
            data, _ = s.recvfrom(48)
            t = unpack("!I", data[40:44])[0] - 2208988800  # convert to Unix time; magic number is 1970 offset
            return t
        except (OSError, ValueError, IndexError):
            # Expected failure modes: network, DNS, short packet
            # just allow it to continue; the time_synced flag will stay false so that it will retry
            return None
        except Exception:
            # struct.error could occur on the unpack method, but it was causing issues for me on the Pico
            # I know this is silly to just do the same thing on the broad Exception, but it's the safest bet
            return None
        finally:
            s.close()

    def create_watchdog(self, timeout_ms: int):
        if self.watchdog_enabled:
            self.wdt = WDT(timeout=timeout_ms)

    def feed_watchdog(self):
        if self.watchdog_enabled:
            self.wdt.feed()

    def ds18x20_scan(self) -> list[bytes]:
        return self.ds18x20.scan()

    def ds18x20_read_temp(self, rom: bytes) -> float:
        return self.ds18x20.read_temp(rom)

    def ds18x20_convert_temp(self):
        self.ds18x20.convert_temp()

    def load_json(self, json_readable_bytes) -> dict:
        return load_json(json_readable_bytes)

    def localtime(self, linux_time_seconds: int = None):
        if linux_time_seconds is None:
            return localtime()
        return localtime(linux_time_seconds)

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
