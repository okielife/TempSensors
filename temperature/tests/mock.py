__print__ = False


###### machine
class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 0

    # noinspection PyUnusedLocal
    def __init__(self, pin_id: int | str, direction: int = IN, pull: int = 0):
        self.pin_id = pin_id
        self.value_on = False

    def on(self) -> None:
        if __print__:  # pragma: no cover
            print(f"Pin #{self.pin_id} on")

    def off(self) -> None:
        if __print__:  # pragma: no cover
            print(f"Pin #{self.pin_id} off")

    def toggle(self) -> None:
        self.value_on = not self.value_on
        if __print__:  # pragma: no cover
            print(f"Pin #{self.pin_id} toggled, now {self.value_on}")


class SPI:
    __throw__ = False

    # noinspection PyUnusedLocal
    def __init__(self, _id: int, baudrate: int, polarity: int, phase: int, sck: Pin, mosi: Pin):
        if SPI.__throw__:
            raise Exception("SPI failed to initialize")


class RTC:
    __throw__ = False

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]):
        if RTC.__throw__:
            raise Exception()
        year, month, day, weekday, hours, minutes, seconds, sub_seconds = timestamp
        if __print__:  # pragma: no cover
            print(f"RTC clock set to: {year}-{month}-{day} {hours}:{minutes}:{seconds}")


class WDT:
    # noinspection PyUnusedLocal
    def __init__(self, timeout: int):
        pass

    def feed(self):
        pass


###### onewire
class OneWire:
    # noinspection PyUnusedLocal
    def __init__(self, pin: Pin):
        if __print__:  # pragma: no cover
            print(f"OneWire class instantiated on pin {pin}")


class OneWireError(Exception):
    pass


###### ds18x20
class DS18X20:
    __missing_entry__ = False
    __read_failure__ = False

    # noinspection PyUnusedLocal
    def __init__(self, ow: OneWire):
        pass

    # noinspection PyMethodMayBeStatic
    def scan(self) -> list[bytes]:
        if DS18X20.__missing_entry__:
            return []
        return [b'(\x93d[\x00\x00\x00\xb4', b'(\xa7\x0fF\xd48h:']

    def convert_temp(self) -> None:
        pass

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def read_temp(self, rom: bytes) -> float:
        if DS18X20.__read_failure__:
            raise Exception()
        import random
        t = random.randint(-20, 40)
        if __print__:  # pragma: no cover
            print(f"Reading temperature as {t} Celsius")
        return t


###### network
STA_IF = 0


class WLAN:
    __connected__ = True

    # noinspection PyUnusedLocal
    def __init__(self, station: int):
        self.activated = False
        self.connected = False
        self.ip = ''
        self.ssid = ''
        self.pw = ''
        self.known_ssids = ["MiFi8000-C1DE", "EmeraldWiFi"]

    # noinspection PyUnusedLocal
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
        if not WLAN.__connected__:
            return
        # return
        if ssid in self.known_ssids:
            self.connected = True
            self.ssid = ssid
            self.pw = pw
            self.ip = '127.0.0.1'


###### time
clock = None


def ticks_ms():
    from time import time
    global clock
    if clock is None:
        clock = time() * 1000
    return int(time() * 1000 - clock)


# noinspection PyUnusedLocal
def ticks_diff(end_time: int, start_time: int) -> int:
    return end_time - start_time


# noinspection PyUnusedLocal
def localtime(time_stamp: int = -1) -> tuple[int, int, int, int, int, int, int]:
    return 2025, 1, 19, 10, 55, 29, 1


###### urequests
class Response:
    __throw__ = False

    def __init__(self):
        if Response.__throw__:
            raise Exception()
        self.status_code = 200
        self.raw = "\b2010"

    def close(self) -> None:
        pass


# noinspection PyUnusedLocal
def get(url: str):
    return Response()


# noinspection PyUnusedLocal
def put(_: str, headers: dict, json: dict):
    return Response()


###### ujson
def load(_) -> dict:
    return {
        "sensors": {
            "03": {
                "hex": "2893645b000000b4",
                "short_name": "Em Garage Fridge",
            },
            "13": {
                "hex": "28a70f46d438683a",
                "short_name": "Em Garage Freezer",
            }
        },
        "rom_hex_to_cable_number": {
            "2893645b000000b4": "03",
            "28a70f46d438683a": "13"
        },
    }


# st7735r
class TFTColor:
    pass


class TFT:
    BLACK = 0
    WHITE = 0
    RED = 0
    GREEN = 0
    BLUE = 0
    YELLOW = 0
    GRAY = 0

    # noinspection PyUnusedLocal,PyPep8Naming
    def __init__(self, spi=None, aDC=None, aReset=None, aCS=None, ScreenSize=(128, 160)):
        pass

    def initr(self):
        pass

    def rgb(self, _):
        pass

    def fill(self, color):
        pass

    def circle(self, point, radius, color):
        pass

    def text(self, point, text, color, font, size=1, nowrap=True):
        pass

    def rect(self, p1, p2, color):
        pass

    def fillrect(self, point, size, color):
        pass

    def hline(self, point, length, color):
        pass

    def vline(self, point, length, color):
        pass
