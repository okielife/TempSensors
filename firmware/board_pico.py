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
    """
    This class implements the controller API using actual hardware calls to the
    Pico board via MicroPython.  This is generally a thin class, whose role is mostly
    to just courier data back and forth once constructed.
    """

    #: The Pico pin where the DS18x20 sensors are wired
    ONE_WIRE_SENSOR_PIN = 28
    #: The Pico pin controlling developer mode: jump pin GP14 over to GND
    DEV_MODE_PIN = 14

    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        """
        Constructs a Pico hardware and MicroPython based controller instance.
        This implementation will handle hardware (Pin, etc.) interactions and network functionality by communicating
        directly to MicroPython and abstracting the functionality through the controller API.
        """
        dev_pin = Pin(BoardPico.DEV_MODE_PIN, Pin.IN, Pin.PULL_UP)
        self.watchdog_enabled = (dev_pin.value() == 1)
        self.wlan = WLAN(STA_IF)
        self.wdt = None
        self._led = Pin('LED', Pin.OUT)
        self.pins = {}
        ow = OneWire(Pin(BoardPico.ONE_WIRE_SENSOR_PIN))
        self.ds18x20 = DS18X20(ow)

    def developer_mode(self) -> bool:
        """
        Returns whether the board is in developer mode.  For this hardware board, the decision is based
        on the developer pin being jumped.

        :return: True or False whether the board is in developer mode
        """
        return not self.watchdog_enabled

    def active(self, active: bool) -> None:
        """
        Sets the Wi-Fi chip and system active status.  If active, it is ready to connect or
        create a network access point.

        :param active: The desired active mode, either True or False
        :return: Nothing
        """
        self.wlan.active(active)

    def isconnected(self) -> bool:
        """
        Returns whether the Wi-Fi system is connected to a network.

        :return: True or False if connected or not.
        """
        return self.wlan.isconnected()

    def ifconfig(self) -> tuple[str, str, str, str]:
        """
        Returns ifconfig information

        :return: A tuple of network configuration: (IP, Subnet, Gateway, DNS)
        """
        return self.wlan.ifconfig()

    def config(self, key: str) -> str:
        """
        Returns a single configuration variable for the given key, such as 'ssid'

        :param key: The configuration key name
        """
        return self.wlan.config(key)

    def scan(self) -> list[tuple]:
        """
        Scans for Wi-Fi networks, returning a list of network instances.

        :return: A list of network tuples, where each contains: (ssid, bssid, channel, RSSI, security, hidden)
        """
        return self.wlan.scan()

    def connect(self, ssid: str, pw: str) -> None:
        """
        Attempts to connect to the specified Wi-Fi network.

        :param ssid: The Wi-Fi network ssid (name)
        :param pw: The Wi-Fi network password
        :return: Nothing
        """
        return self.wlan.connect(ssid, pw)

    def http_get(self, url: str):
        """
        Attempts to dispatch an HTTP GET request to the specified URL using the urequests library.

        :param url: The url to request
        :return: A Response object, including status code and response data.
        """
        return get(url)

    def http_put(self, url: str, headers: dict, json: dict):
        """
        Attempts to dispatch an HTTP PUT request to the specified URL using the urequests library,
        with given headers and JSON payload.

        :param url: The url to request
        :param headers: Additional data, which could include branch name, data mime type, authentication, etc.
        :param json: A dict payload to submit with the PUT request
        :return: A Response object, including status code and response data.
        """
        return put(url, headers=headers, json=json)

    # noinspection PyUnusedLocal
    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]) -> None:
        """
        Attempts to set the Pico's Real Time Clock (RTC) to the specified timestamp.

        :param timestamp: A timestamp of (year, month, day, weekday, hour, minute, second, microsecond)
        :return: Nothing
        """
        RTC().datetime(timestamp)

    def get_ntp_timestamp(self) -> int | None:
        """
        Attempts to read the current Linux timestamp from an NTP server (pool.ntp.org).  The Linux timestamp
        is calculated based on the NTP response timestamp.

        :return: Returns the Linux timestamp (seconds since epoch) if successful, otherwise returns None
        """
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

    def create_watchdog(self, timeout_ms: int) -> None:
        """
        If developer mode is active, nothing is done here.  For normal operation, this will create the system
        watchdog.  This watchdog must be fed regularly before the timeout is reached.  if not fed, it will
        force the whole system to reboot.  Note that this means if you intend to perform a sleep while the watchdog
        is active, you need to do it in a loop and regularly feed the watchdog to avoid a system reset.

        :param timeout_ms: The target interval, or timeout, between feedings.
        :return: Nothing
        """
        if self.watchdog_enabled:
            self.wdt = WDT(timeout=timeout_ms)

    def feed_watchdog(self) -> None:
        """
        If developer mode is active, nothing is done here, because there is no watchdog on patrol.
        For normal operation, the watchdog is fed, resetting the timer back to zero.

        :return: Nothing
        """
        if self.watchdog_enabled:
            self.wdt.feed()

    def ds18x20_scan(self) -> list[bytes]:
        """
        Performs a scan of one-wire DS18x20 connected to the board, returning sensor IDs

        :return: A list of ROMs connected to the device, each as a bytes variable.
        """
        return self.ds18x20.scan()

    def ds18x20_read_temp(self, rom: bytes) -> float:
        """
        Reads the temperature from the specific DS18x20 ROM scratchpad.

        :param rom: The ROM for the sensor of interest, as bytes.
        :return: The temperature, in degrees Celsius.
        """
        return self.ds18x20.read_temp(rom)

    def ds18x20_convert_temp(self):
        """
        Asks all DS18x20 devices connected to the one-wire pin to refresh the latest temperature in their scratchpad.

        Must be called before reading temperatures, and give at least 750 ms in between.

        :return: Nothing
        """
        self.ds18x20.convert_temp()

    def load_json(self, json_readable_bytes) -> dict:
        """
        Reads from the provided JSON bytes read-able object using the ujson library, and provides a Python dict.

        :param json_readable_bytes: A read-able object of JSON content bytes, such as a file opened with 'rb'
        :return: A Python dict representing the JSON content
        """
        return load_json(json_readable_bytes)

    def localtime(self, linux_time_seconds: int = None):
        """
        Converts the provided Linux time, or the converted time if passed in, into a tuple of timestamp values.

        :param linux_time_seconds: Number of seconds since the Epoch; a Linux timestamp.
        :return: A tuple timestamp, with (year, month, day, hour, minute, second, weekday, year-day)
        """
        if linux_time_seconds is None:
            return localtime()
        return localtime(linux_time_seconds)

    def ticks_ms(self) -> int:
        """
        Returns an increasing millisecond counter, used for checking durations, not absolute time. It may overflow.
        Be sure to use ticks_diff to help support the condition of overflow.

        :return: An integer timestamp, milliseconds since some arbitrary but fixed time for a given boot.
        """
        return ticks_ms()

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        """
        Calculates the difference between two ticks, including ring arithmetic to try to handle wrap-around scenarios.

        :param milliseconds_a: Higher of the two values returned from ticks_ms
        :param milliseconds_b: Lower of the two values returned from ticks_ms
        :return: Effectively just milliseconds_a - milliseconds_b but attempts to handle wrap-around scenarios.
        """
        return ticks_diff(milliseconds_a, milliseconds_b)

    def system_hang(self, seconds: int = None):
        """
        Provides a single place for causing the system to "hang" for either an amount of seconds, or forever.

        There are some scenarios where the system may need to hang for a few seconds, such as if an error pops up, and
        you want to hold the sensor for 30 seconds then let the machine reboot.  That way the message may be seen on the
        sensor.  In that case, call this with a positive integer number of seconds.  The machine will hang that long,
        feeding the watchdog as needed to ensure the machine does not reboot during this hang.

        There are some scenarios where the system may need to hang forever, such as if the sensor initialization fails
        immediately upon boot.  In that case, call this with no argument, or None.  The machine will hang forever,
        feeding the watchdog as needed to ensure the machine does not reboot automatically.

        :param seconds: Number of seconds to hang, or None to hang forever
        :return: Nothing
        """
        if seconds is None:
            while True:
                sleep(1)
                self.feed_watchdog()
        else:
            for i in range(seconds):
                sleep(1)
                self.feed_watchdog()

    def sleep(self, seconds: float):
        """
        Sleeps the system for the specified amount of time. The watchdog is fed throughout the time to ensure
        the system does not reboot.

        :param seconds: The floating point number of seconds to sleep.
        :return: Nothing
        """
        if seconds > 3:
            for i in range(int(seconds)):
                sleep(1)
                self.feed_watchdog()
        else:
            sleep(seconds)

    def run_forever(self) -> bool:
        """
        Returns whether this controller should actually run "forever".  For this Pico hardware board,
        the answer is yes, the sensing system should run continually.

        :return: True
        """
        return True

    def print(self, message: str):
        """
        Prints the given message to the console, if connected, otherwise this just goes to sys.stdout, which
        will be a void USB serial device where the content is briefly buffered then vanishes.

        :param message: A string message to print.
        :return: Nothing
        """
        print(message)
