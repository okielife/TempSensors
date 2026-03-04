class ResponseBase:
    """This defines the required needs of an HTTP response; from an actual hardware HTTP response, or a mock."""

    def __init__(self) -> None:
        #: HTTP status code, like 200 or 401
        self.status_code = 0
        #: HTTP response as string text
        self.text = ""
        #: HTTP response as raw bytes
        self.raw = b""

    def close(self) -> None:
        """HTTP response objects have a close method that we use, so any response mocks need to implement their own."""
        raise NotImplementedError


class PinBase:
    """This defines the required needs of a controller Pin; such as setting, reading, and toggling values."""

    # noinspection PyUnusedLocal
    def __init__(self, pin_id: str | int, direction: int = 0, pull: int = 0) -> None:
        """
        Creates a new Pin object with given ID and optional parameters

        :param pin_id: The ID associated with the Pin, could be string or integer
        :param direction: The IN/OUT signal for whether the pin is a sensor or actuator
        :param pull: The pull state of the Pin whether it is pulled to VCC or GND.
        """
        pass

    def on(self) -> None:
        """Sets the pin to an ON state."""
        raise NotImplementedError

    def off(self) -> None:
        """Sets the pin to an OFF state."""
        raise NotImplementedError

    def toggle(self) -> None:
        """Toggles the pin between ON and OFF states."""
        raise NotImplementedError

    def value(self) -> int:
        """
        Gets the current ON/OFF value of the Pin.
        :return: 1 if the Pin is ON, 0 otherwise
        """
        raise NotImplementedError


class BoardBase:
    """This class defines the required controller API.

    The hardware runs via MicroPython, and this class enables different controller
    derived classes to run in MicroPython or CPython either way.  Anything the sensing
    logic would expect to get from the controller, including network, terminal, and
    system attributes, is abstracted with this base class.
    """

    # noinspection PyUnusedLocal
    def __init__(self) -> None:
        self.printed_messages_for_testing = ""

    def developer_mode(self) -> bool:
        """
        Returns whether the board is in developer mode.

        :return: True or False whether the board is in developer mode
        """
        raise NotImplementedError

    def active(self, active: bool) -> None:
        """
        Sets the Wi-Fi system active mode.

        :param active: The desired active mode, True or False
        """
        raise NotImplementedError

    def isconnected(self) -> bool:
        """
        Returns whether the Wi-Fi system is connected to a network.
        :return: True or False if connected or not.
        """
        raise NotImplementedError

    def ifconfig(self) -> tuple[str, str, str, str]:
        """
        Returns ifconfig information
        :return: A tuple of network configuration: (IP, Subnet, Gateway, DNS)
        """
        raise NotImplementedError

    def config(self, key: str) -> str:
        """
        Returns a single configuration variable for the given key

        :param key: The configuration key name
        """
        raise NotImplementedError

    def scan(self) -> list[tuple[bytes, bytes, int, int, int, int]]:
        """
        Scans for Wi-Fi networks, returning a list of network instances.

        :return: A list of network tuples, where each contains: (ssid, bssid, channel, RSSI, security, hidden)
        """
        raise NotImplementedError

    def connect(self, ssid: str, pw: str) -> None:
        """
        Attempts to connect to the specified Wi-Fi network.

        :param ssid: The Wi-Fi network ssid (name)
        :param pw: The Wi-Fi network password
        :return: Nothing
        """
        raise NotImplementedError

    def http_get(self, url: str) -> ResponseBase:
        """
        Attempts to dispatch an HTTP GET request to the specified URL.

        :param url: The url to request
        :return: A Response object, including status code and response data.
        """
        raise NotImplementedError

    def http_put(self, url: str, headers: dict, json: dict) -> ResponseBase:
        """
        Attempts to dispatch an HTTP PUT request to the specified URL, with given headers and JSON payload.

        :param url: The url to request
        :param headers: Additional data, which could include branch name, data mime type, authentication, etc.
        :param json: A dict payload to submit with the PUT request
        :return: A Response object, including status code and response data.
        """
        raise NotImplementedError

    def rtc_datetime(self, timestamp: tuple[int, int, int, int, int, int, int, int]) -> None:
        """
        Attempts to set the Real Time Clock (RTC) to the specified timestamp.

        :param timestamp: A timestamp of (year, month, day, weekday, hour, minute, second, microsecond)
        :return: Nothing
        """
        raise NotImplementedError

    def get_ntp_timestamp(self) -> int | None:
        """
        Attempts to read the current Linux timestamp from an NTP server.

        :return: Returns the Linux timestamp (seconds since epoch) if successful, otherwise returns None
        """
        raise NotImplementedError

    def create_watchdog(self, timeout_ms: int) -> None:
        """
        Creates a CPU watchdog.  On actual hardware it will need to be fed regularly, or it will reset the device.

        :param timeout_ms: The amount of time in ms to set for the watchdog.
        :return: Nothing
        """
        raise NotImplementedError

    def feed_watchdog(self) -> None:
        """
        Feeds the CPU watchdog (if it exists), to reset the timer back to full.

        :return: Nothing
        """
        raise NotImplementedError

    def ds18x20_scan(self) -> list[bytes]:
        """
        Performs a scan of one-wire DS18x20 connected to a specific machine Pin, returning sensor IDs

        :return: A list of ROMs connected to the device, each as a bytes variable.
        """
        raise NotImplementedError

    def ds18x20_read_temp(self, rom: bytes) -> float:
        """
        Reads the temperature from the specific DS18x20 ROM scratchpad.

        :param rom: The ROM for the sensor of interest, as bytes.
        :return: The temperature, in degrees Celsius.
        """
        raise NotImplementedError

    def ds18x20_convert_temp(self) -> None:
        """
        Asks all DS18x20 devices connected to the one-wire pin to refresh the latest temperature in their scratchpad.

        Must be called before reading temperatures, and give at least 750 ms in between.

        :return: Nothing
        """
        raise NotImplementedError

    def load_json(self, json_readable_bytes) -> dict:  # type: ignore[no-untyped-def]
        """
        Reads from the provided JSON bytes read-able object and provides a Python dict

        :param json_readable_bytes: A read-able object of JSON content bytes, such as a file opened with 'rb'
        :return: A Python dict representing the JSON content
        """
        raise NotImplementedError

    def localtime(self, linux_time_seconds: int | None = None) -> tuple:
        """
        Converts the provided Linux time into a tuple of timestamp values.

        :param linux_time_seconds: Number of seconds since the Epoch; a Linux timestamp.
        :return: A tuple timestamp, with (year, month, day, hour, minute, second, weekday, year-day)
        """
        raise NotImplementedError

    def ticks_ms(self) -> int:
        """
        Returns an increasing millisecond counter, used for checking durations, not absolute time. It may overflow.

        :return: An integer timestamp, milliseconds since some arbitrary but fixed time.
        """
        raise NotImplementedError

    def ticks_diff(self, milliseconds_a: int, milliseconds_b: int) -> int:
        """
        Calculates the difference between two ticks, including ring arithmetic to try to handle wrap-around scenarios.

        :param milliseconds_a: Higher of the two values returned from ticks_ms
        :param milliseconds_b: Lower of the two values returned from ticks_ms
        :return: Effectively just milliseconds_a - milliseconds_b but attempts to handle wrap-around scenarios.
        """
        raise NotImplementedError

    def system_hang(self, seconds: int | None = None) -> None:
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
        raise NotImplementedError

    def sleep(self, seconds: float) -> None:
        """
        Sleeps the system for the specified amount of time.

        :param seconds: The floating point number of seconds to sleep.
        :return: Nothing
        """
        raise NotImplementedError

    def run_forever(self) -> bool:
        """
        Returns whether this controller should actually run "forever".

        In some derived classes, such as unit tests, you don't actually want the machine to run forever.  This function
        allows each controller implementation to define their own behavior.

        :return: True if this controller should run forever, False otherwise
        """
        raise NotImplementedError

    def print(self, message: str) -> None:
        """
        Prints the given message to the console provided by the controller implementation.

        :param message: A string message to print.
        :return: Nothing
        """
        raise NotImplementedError
