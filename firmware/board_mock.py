from datetime import datetime
from time import time
from typing import Any

from firmware.board_base import BoardBase, ResponseBase, PinBase


class ResponseMock(ResponseBase):
    """
    This mock response class implements the response API, but with behavior easily set up for testing.
    """

    # noinspection PyMissingConstructor
    def __init__(self, throw: bool = False, bad_status: bool = False) -> None:
        """
        Constructor of the mock response class

        :param throw: If true, then this constructor will throw, simulating an error during HTTP response creation.
        :param bad_status: If true, then this response will have an erroneous (400) status code.
        """
        if throw:
            raise Exception()
        #: The status_code can be overridden by passing a bad_status
        self.status_code = 400 if bad_status else 200
        self.text = ""
        self.raw = b""

    def close(self) -> None:
        """
        Since this response class is not actually holding any data, this does nothing

        :return: Nothing
        """
        return


class PinMock(PinBase):
    """
    This mock Pin class implements the required Pin API, with just enough implementation to mimic for testing.
    """
    #: A Pin IN value indicates the pin is in a sensor mode, awaiting data, such as for buttons
    IN = 0
    #: A Pin OUT value indicates the pin mode is being driven from the board, such as for LEDs
    OUT = 1
    #: PULL_UP indicates the pin is pulled up to VCC through a small resistor, yielding a 'high' value
    PULL_UP = 0

    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(self, pin_id: str | int, direction: int = IN, pull: int = 0) -> None:
        """
        Creates a mock Pin object, which is essentially just an on/off signal.

        :param pin_id: Unused in this mock class
        :param direction: Unused in this mock class
        :param pull: Unused in this mock class
        """
        self.value_on = False

    def on(self) -> None:
        """Sets the pin to an ON state."""
        self.value_on = True

    def off(self) -> None:
        """Sets the pin to an OFF state."""
        self.value_on = False

    def toggle(self) -> None:
        """Toggles the pin between ON and OFF states."""
        self.value_on = not self.value_on

    def value(self) -> int:
        """
        Gets the current ON/OFF value of the Pin.
        :return: 1 if the Pin is ON, 0 otherwise
        """
        return 1 if self.value_on else 0


class BoardMock(BoardBase):
    """
    This mock board class implements the required board API, with just enough implementation to mimic for testing.
    """
    # noinspection PyUnusedLocal
    def __init__(self, watchdog_enabled: bool = True, verbose: bool = False, throw_rtc: bool = False,
                 throw_http: bool = False, bad_http_get_status: bool = False, bad_http_put_status: bool = False,
                 wifi_connect: bool = True, ds18x20_read_failure: bool = False,
                 continue_running_after_first_iteration: bool = False, fixed_temperature_c: float = 1000,
                 convert_temp_failure: bool = False, bad_ntp_timestamp: bool = False,
                 label_missing_from_rom_hex_map: bool = False, label_missing_from_sensors: bool = False,
                 empty_ds18x20_roms: bool = False, override_wifi_ssids: list | None = None) -> None:
        """
        Constructs a mock board class for unit testing various behaviors, based on the flag arguments

        :param watchdog_enabled: Controls whether the board is in the developer mode
        :param verbose: Controls whether print messages are actually printed to the Python terminal
        :param throw_rtc: Controls whether the RTC clock operations should raise an exception
        :param throw_http: Controls whether the HTTP operation should raise an exception
        :param bad_http_get_status: Controls whether the HTTP GET should return 400 error code
        :param bad_http_put_status: Controls whether the HTTP PUT should return 400 error code
        :param wifi_connect: Controls whether the board should successfully connect to Wi-Fi
        :param ds18x20_read_failure: Controls whether a failure occurs when reading ds18x20 temperature
        :param fixed_temperature_c: Overrides the Celsius temperature sensed by the temperature sensor
        :param convert_temp_failure: Controls whether the ds18x20 encounters an error when converting temp
        :param bad_ntp_timestamp: Controls whether the NTP pool gives a bad timestamp
        :param label_missing_from_rom_hex_map: Controls whether the sensor config has a rom hex missing
        :param label_missing_from_sensors: Controls whether the sensor config has a sensor missing
        :param empty_ds18x20_roms: Controls whether the DS18x20 rom scan should be empty
        :param override_wifi_ssids: A list of Wi-Fi SSIDs to mimic finding in the scan function
        """
        # config flags
        super().__init__()
        self.watchdog_enabled = watchdog_enabled
        self.verbose = verbose
        self.throw_rtc = throw_rtc
        self.throw_http = throw_http
        self.bad_http_get_status = bad_http_get_status
        self.bad_http_put_status = bad_http_put_status
        self.wifi_connect = wifi_connect
        self.ds18x20_read_failure = ds18x20_read_failure
        self.fixed_temperature_c = fixed_temperature_c
        self.convert_temp_failure = convert_temp_failure
        self.bad_ntp_timestamp = bad_ntp_timestamp
        self.label_missing_from_rom_hex_map = label_missing_from_rom_hex_map
        self.label_missing_from_sensors = label_missing_from_sensors
        self.empty_ds18x20_roms = empty_ds18x20_roms
        # state data
        self.activated = False
        self.connected = False
        self.ip = ''
        self.ssid = ''
        self.pw = ''
        self.known_ssids = override_wifi_ssids if override_wifi_ssids else ["WiFiNetworkOne", "HotSpotAlpha"]
        self.watchdog_watching = False
        self.pins: dict = {}
        self.clock = time() * 1000

    def developer_mode(self) -> bool:
        """
        The developer flag is purely based on the passed in watchdog flag

        :return: Developer mode status; default is False,
        """
        return not self.watchdog_enabled

    def active(self, active: bool) -> None:
        """
        Sets the Wi-Fi active status for this mock board

        :param active: The desired active mode, True or False
        :return: Nothing
        """
        self.activated = active

    def isconnected(self) -> bool:
        """
        Returns whether the mock board appears to be connected to the Wi-Fi network.
        If it has not been activated, it will fail.  If it has, it returns whether it is connected.

        :return: True or False if connected or not
        """
        assert self.activated
        return self.connected

    def ifconfig(self) -> tuple[str, str, str, str]:
        """
        Returns a dummy ifconfig of a fake IP plus blanks for the other terms

        :return: A dummy tuple of network configuration (IP, Subnet, Gateway, DNS)
        """
        return self.ip, '', '', ''

    def config(self, key: str) -> str:
        """
        This mock config function is only designed to return the config for 'ssid', other keys will throw an error.

        :param key: The config key to request, which can only be 'ssid' for this mock class
        :return: The config value requested, which can only be the assigned ssid for this mock class
        """
        assert key == 'ssid'
        return self.ssid

    def scan(self) -> list[tuple[bytes, bytes, int, int, int, int]]:
        """
        This mock scan function simply returns a list of Wi-Fi network information with mostly dummy values

        :return: A list of network tuples, where each contains: (ssid, bssid, channel, RSSI, security, hidden)
        """
        return [(x.encode('utf-8'), b"", 0, 0, 2, 0) for x in self.known_ssids]

    def connect(self, ssid: str, pw: str) -> None:
        """
        This mock connect function will connect if the wifi_connect class argument was not False and the
        requested ssid is in the list of known ssids.

        :param ssid: The network ssid
        :param pw: The network password
        :return: Nothing
        """
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
        """
        Mocks an HTTP GET by creating a response object sensitive to control flags.
        If throw_http is active, it will result in an exception.  If bad_http_get_status
        is active, it will return an erroneous status code.

        :param url: The URL to mock a GET request
        :return: A ResponseBase object
        """
        return ResponseMock(self.throw_http, self.bad_http_get_status)

    def http_put(self, url: str, headers: dict, json: dict) -> ResponseBase:
        """
        Mocks an HTTP PUT by creating a response object sensitive to control flags.
        If throw_http is active, it will result in an exception.  If bad_http_put_status
        is active, it will return an erroneous status code.

        :param url: The url to request
        :param headers: Additional data, which could include branch name, data mime type, authentication, etc.
        :param json: A dict payload to submit with the PUT request
        :return: A ResponseBase object
        """
        return ResponseMock(self.throw_http, self.bad_http_put_status)

    # noinspection PyUnusedLocal
    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]) -> None:
        """
        Mocks the RTC datetime assignment by simply unpacking the timestamp argument tuple.
        If throw_rtc is active, it will raise an exception.

        :param timestamp: A timestamp of (year, month, day, weekday, hour, minute, second, microsecond)
        :return: Nothing
        """
        if self.throw_rtc:
            raise OSError()
        year, month, day, weekday, hours, minutes, seconds, sub_seconds = timestamp
        if self.verbose:  # pragma: no cover
            print(f"RTC clock set to: {year}-{month}-{day} {hours}:{minutes}:{seconds}")

    def get_ntp_timestamp(self) -> int | None:
        """
        Mocks the NTP timestamp request by simply returning a Linux timestamp value for the current time.
        If bad_ntp_timestamp is active, it will return None to mimic a bad request.

        :return: A fixed timestamp value or None
        """
        if self.bad_ntp_timestamp:
            return None
        return int(datetime.now().timestamp())  # roughly March 4, 2026

    def create_watchdog(self, timeout_ms: int) -> None:
        """
        Mocks the watchdog creation by setting a flag to indicate that the watchdog is on patrol.

        :param timeout_ms: Not used in this mock class
        :return: Nothing
        """
        self.watchdog_watching = self.watchdog_enabled

    def feed_watchdog(self) -> None:
        """
        Mocks the watchdog feed step, but does not do anything here

        :return: Nothing
        """
        pass

    def ds18x20_scan(self) -> list[bytes]:
        """
        Mocks the DS18x20 scan step to return found sensor ROMs in bytes.
        If the empty_ds18x20_roms flag is active, it will return an empty list.

        :return: A list of byte strings, one for each sensor found.
        """
        if self.empty_ds18x20_roms:
            return []
        return [b'(\x93d[\x00\x00\x00\xb4', b'(\xa7\x0fF\xd48h:']

    def ds18x20_read_temp(self, rom: bytes) -> float:
        """
        Mocks the functionality of reading the temperature for a specific ROM on the one-wire connection.
        If the ds18x20_read_failure flag is active, it will raise an OSError.  If the fixed_temperature_c
        flag was active, then the provided value will be returned.  Otherwise, this returns 20

        :param rom: Not used in this mock class, at this time anyway
        :return: The mocked sensed temperature in Celsius
        """
        if self.ds18x20_read_failure:
            raise OSError()
        if self.fixed_temperature_c != 1000:
            return self.fixed_temperature_c
        return 20

    def ds18x20_convert_temp(self) -> None:
        """
        Mocks the convert_temp functionality, which prepares the DS18x20 sensors for reading.
        If the convert_temp_failure flag is active, this will raise an exception, otherwise it does nothing.

        :return: Nothing
        """
        if self.convert_temp_failure:
            raise Exception("Could not convert temperature")

    def load_json(self, json_readable_bytes) -> dict:  # type: ignore[no-untyped-def]
        """
        Mocks the JSON reading function by simply returning a premade dictionary.
        If label_missing_from_rom_hex_map is active, there will be a missing ROM in the
        hex map.  If the label_missing_from_sensors flag is active, there will be a missing
        sensor in the sensors map.

        :param json_readable_bytes: Not used in this mock class
        :return: A dictionary mimicking the configuration found on the repo
        """
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

    def localtime(self, linux_time_seconds: int | None = None) -> tuple:
        """
        Mocks the localtime function by using datetime to return the current date and time,
        or the converted time if passed in.

        :param linux_time_seconds: An optional Linux timestamp
        :return: The localtime as a tuple (year, month, day, hour, minute, second, weekday, year-day)
        """
        dt = datetime.now() if linux_time_seconds is None else datetime.fromtimestamp(linux_time_seconds)
        return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday()

    def ticks_ms(self) -> int:
        """
        Mocks the ticks_ms function by keeping an internal clock and reporting the ms since it was created.

        :return: An increasing number of milliseconds.
        """
        return int(time() * 1000 - self.clock)

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        """
        Mocks the ticks_diff function by always returning a large value, indicating time has passed.
        In the real function, there is functionality to try to handle time overflow for large values.

        :param milliseconds_a: The larger value from ticks_ms
        :param milliseconds_b: The smaller value from ticks_ms
        :return: In this mock class, this returns a fixed large value
        """
        return 1_000_000  # TODO: Control this a little better

    def system_hang(self, seconds: int | None = None) -> None:
        """
        The real system_hang function can hold indefinitely or for a fixed time.  This mock function
        handles the finite time version by simply returning - not waiting.  This mock function handles
        the infinite hang by calling an exception.

        :param seconds: An optional number of seconds to hang.  If None, an exception will be raised.
        :return: Nothing
        """
        if seconds is None:
            raise RuntimeError("Mocking the sensor box infinite system hang with an exception")
        # if there was a short positive hang, then it just returns

    def sleep(self, seconds: float) -> None:
        """
        Mocks the sleep functionality by doing nothing.

        :param seconds: Ignored in this mock class
        :return: Nothing
        """
        return

    def run_forever(self) -> bool:
        """
        Specifies the run_forever mode for this mock class as False.

        :return: Bool of False for this mock class
        """
        return False

    def print(self, message: str) -> None:
        """
        Mocks the print functionality by tracking the printed messages in a variable.
        This can be inspected by unit tests to ensure messages were printed to the terminal.

        :param message: Message to be printed
        :return: Nothing
        """
        self.printed_messages_for_testing += message
