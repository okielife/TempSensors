# these imports are fine whether we are running on regular Python or MicroPython
from binascii import b2a_base64
from socket import getaddrinfo, socket, AF_INET, SOCK_DGRAM
from struct import unpack


class OperatingMode:  # enum is not available in micropython
    NormalRun = 1  # in this mode, we run everything completely normally, including the watchdog
    DebugHardware = 2  # in this mode, we run everything normally, except we don't include the watchdog
    UnitTesting = 3  # in this mode, we mock everything, and do not try to instantiate anything tk
    MockWindow = 4  # in this mode, we run the mock TFT in an actual little tk window locally, other


# the other imports need to either be mocked or found from the nested temperature package when running locally
try:  # pragma: no cover
    from ds18x20 import DS18X20
    # noinspection PyPackageRequirements
    from machine import Pin, SPI, RTC, WDT
    # noinspection PyPackageRequirements
    from network import WLAN, STA_IF
    # noinspection PyPackageRequirements
    from onewire import OneWire, OneWireError
    from time import ticks_ms, ticks_diff, localtime
    # noinspection PyPackageRequirements
    from urequests import get, put
    # noinspection PyPackageRequirements
    from ujson import load as load_json
    from st7735 import FONT
    from config import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN
except ImportError:
    from temperature.tests.mock import DS18X20  # ds18x20
    from temperature.tests.mock import Pin, SPI, RTC, WDT  # machine
    from temperature.tests.mock import WLAN, STA_IF  # network
    from temperature.tests.mock import OneWire, OneWireError  # onewire
    from temperature.tests.mock import ticks_ms, ticks_diff, localtime  # time
    from temperature.tests.mock import get, put  # urequests
    from temperature.tests.mock import load as load_json  # ujson
    from temperature.tests.mock import FONT
    from temperature.config_template import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN

__version__ = 3
__revision__ = 7

__diagram__ = """
  Looking at the Pico from "above", so that you can see the WiFi antenna
                ┏━━━━┓USB CONNECTION
          ┌─────┃    ┃─────┐
 GP0  | 01│     ┗━━━━┛     │40 | VBUS
 GP1  | 02│                │39 | VSYS
 GND  | 03│                │38 | GND
 GP2  | 04│     ╭─╮        │37 | 3V3_EN
 GP3  | 05│     │ │        │36 | 3V3(OUT)  - SPLIT TO SCREEN VCC and SENSOR VCC
 GP4  | 06│     ╰─╯        │35 | ADC_VREF
 GP5  | 07│                │34 | GP28  - SENSOR DAT
 GND  | 08│                │33 | GND   - SENSOR GND
 GP6  | 09│    ┌─────┐     │32 | GP27
 GP7  | 10│    │     │     │31 | GP26
 GP8  | 11│    │     │     │30 | RUN
 GP9  | 12│    └─────┘     │29 | GP22  - DEBUG JUMPER 1
 GND  | 13│                │28 | GND   - DEBUG JUMPER 2
 GP10 | 14│                │27 | GP21  - SCREEN LED+
 GP11 | 15│                │26 | GP20  - SCREEN RESET
 GP12 | 16│                │25 | GP19  - SCREEN SDA
 GP13 | 17│                │24 | GP18  - SCREEN SCL
 GND  | 18│                │23 | GND   - SCREEN GND
 GP14 | 19│                │22 | GP17  - SCREEN CS
 GP15 | 20│                │21 | GP16  - SCREEN A0/DC
          └────────────────┘

  Looking at the TFT screen from below, where you can see the SD card slot
   ┌─────────────────────────────────────────────────────────────┐
   │                  ┌─────────────────────────────┐            │ LED-
   │                  │                             │            │ LED+  - PICO GP21
   │                  │                             │            │ SD_CS
   │                  │                             │            │ MOSI
   │                   ╲                            │            │ MISO
   │                    │                           │            │ SCK
   │                    │                           │            │ CS    - PICO GP17
   │                    └───────────────────────────┘            │ SCL   - PICO GP18
   │                                                             │ SDA   - PICO GP19
   │                                                             │ A0    - PICO GP16
   │                                                             │ RESET - PICO GP20
   │                                                             │ NC
   │                                                             │ NC
   │                                                             │ NC
   │                                                             │ VCC   - SPLITTER FROM PICO 3V3
   │                                                             │ GND   - PICO GND
   └─────────────────────────────────────────────────────────────┘
"""


class Sensor:
    def __init__(self, rom: bytes, label: str):
        self.rom = rom
        self.temperature_f = None
        self.label = label
        self.name = "UNKNOWN_NAME"
        self.active = False


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)


class SensorBox:
    WIDTH = 128
    HEIGHT = 160
    PIN_DC = 16
    PIN_CS = 17
    PIN_SCI_SCK = 18
    PIN_SDA_MOSI = 19
    PIN_RESET = 20
    PIN_LED = 21

    # noinspection PyPep8Naming
    def __init__(self, TFTClass: type, operating_mode: int = OperatingMode.NormalRun):
        # Unfortunately, this SensorBox will be acting different based on the current scenario
        # I will try to keep that to a minimum to avoid complexity in here. But there will likely
        # be a few cases that I want to handle different.  For example, I do not want to accumulate
        # the printed messages when running normally, or we would hit memory issues.  So only
        # accumulate those when unit testing.
        self.mode = operating_mode
        self.printed_messages_for_testing = ""
        self.displayed_messages_for_testing = ""

        # set up the watchdog right away as needed
        self.wdt = WDT(timeout=8000)

        # basic member variables
        self.last_temp_stamp = None
        self.last_push_stamp = None
        self.last_push_had_errors = False
        self.last_push_ms = 0
        self.time_synced = False
        self.retrieved_sensor_info = False

        # init the onboard LED as a basic means of communicating status
        self.led = Pin("LED", Pin.OUT)

        post_y_starting = 0
        post_y_version = 18
        post_y_screen = 36
        post_y_sensors = 54
        post_y_wifi = 72
        post_y_clock = 90
        post_y_date = 108
        post_y_config = 126
        post_y_booting = 144

        # init the TFT base class to get a terminal first
        try:
            spi = SPI(0, baudrate=20000000, polarity=0, phase=0, sck=Pin(self.PIN_SCI_SCK), mosi=Pin(self.PIN_SDA_MOSI))
            self.tft = TFTClass(
                spi, aDC=self.PIN_DC, aReset=self.PIN_RESET, aCS=self.PIN_CS, ScreenSize=(self.WIDTH, self.HEIGHT)
            )
            self.tft.initr()
            Pin(self.PIN_LED, Pin.OUT).on()
            self.tft.rgb(False)
            self.tft.fill(Color.BLACK)
        except Exception as e:
            self.print(f"Could not initialize display: {e}")  # pragma: no cover
            if self.mode == OperatingMode.UnitTesting:
                raise e from None
            # just hang here forever, we can't go on without a screen, obviously not covering this with unit tests
            while True:  # pragma: no cover
                self.flash_led(3)
                self.sleep(2)
                self.wdt.feed()
        self.display_text((15, post_y_starting), "STARTING", Color.GREEN, 2)
        self.display_text((0, post_y_version), f"Version {__version__}.{__revision__}", Color.WHITE, 2)
        self.display_text((0, post_y_screen), "Screen:  OK", Color.WHITE, 2)
        self.wdt.feed()

        # set up the sensors now
        ow = OneWire(Pin(28))
        self.ds = DS18X20(ow)
        scanned_roms = {rom.hex(): rom for rom in self.ds.scan()}
        self.wdt.feed()
        missing = [label for label, hex_id in CONNECTED_SENSORS if hex_id not in scanned_roms]
        if missing:
            self.show_fatal_error(f"Could not initialize sensor(s): {', '.join(missing)}; check connections")
            if self.mode == OperatingMode.UnitTesting:
                raise Exception()
            else:  # pragma: no cover
                # just hang here forever, we don't want to continue without the sensors
                while True:
                    self.sleep(2)
                    self.wdt.feed()
        self.sensors = [Sensor(scanned_roms[hex_id], label) for label, hex_id in CONNECTED_SENSORS]
        self.display_text((0, post_y_sensors), "Sensors: OK", Color.WHITE, 2)
        self.wdt.feed()

        # init the Wi-Fi and try to sync the clock
        self.wlan = WLAN(STA_IF)
        self.wlan.active(True)
        self.ip = ""
        self.ssid = ""
        if not self.wlan.isconnected():
            self.try_to_connect_to_wifi()
        if self.wlan.isconnected():
            self.ip, _, _, _ = self.wlan.ifconfig()
            self.ssid = self.wlan.config('ssid')
            self.display_text((0, post_y_wifi), "Wi-Fi:   OK", Color.WHITE, 2)
            self.try_to_sync_time()
            if self.time_synced:
                t = localtime()
                self.display_text((0, post_y_clock), "Clock:   OK", Color.WHITE, 2)
                self.display_text((0, post_y_date), "Date: {:02d}/{:02d}".format(t[1], t[2]), Color.WHITE, 2)
            else:
                self.show_fatal_error("CLOCK SYNC ERROR, will continue to boot in 5 seconds and retry sync later.")
                self.sleep(5)
            self.try_to_get_sensor_details()
            if self.retrieved_sensor_info:
                self.display_text((0, post_y_config), "Config:  OK", Color.WHITE, 2)
            else:
                self.display_text((0, post_y_config), "Config: ERR", Color.RED, 2)
                self.show_fatal_error(
                    "Could not retrieve sensor config data from GitHub, "
                    "will continue to boot in 5 seconds and retry later."
                )
                self.sleep(5)
        else:
            self.display_text((0, post_y_wifi), "Wi-Fi:  NOT", Color.YELLOW, 2)
            self.display_text((0, post_y_clock), "READY, CHECK", Color.YELLOW, 2)
            self.display_text((0, post_y_date), "NETWORK", Color.YELLOW, 2)
            self.display_text((0, post_y_config), "WILL RETRY", Color.YELLOW, 2)
            self.sleep(2)
        self.wdt.feed()

        self.display_text((0, post_y_booting), "BOOTING UP!", Color.WHITE, 2)
        self.wdt.feed()

    def run(self):
        github_push_interval_ms = 3_600_000
        self.wdt.feed()
        first_time = True
        while True:
            try:
                self.update_temperatures()
                self.wdt.feed()
                self.last_temp_stamp = localtime()
                if not self.wlan.isconnected():
                    # try to connect, but if we can't, just continue to updating temps and looping
                    self.try_to_connect_to_wifi()
                    self.wdt.feed()
                if self.wlan.isconnected():
                    if not self.time_synced:
                        self.try_to_sync_time()
                        self.wdt.feed()
                    if not self.retrieved_sensor_info:
                        self.try_to_get_sensor_details()
                    # we don't necessarily need the sensor extra info to push to GitHub,
                    # so no need to check if self.retrieved_sensor_info
                    reached_push_time = ticks_diff(ticks_ms(), self.last_push_ms) > github_push_interval_ms
                    if self.time_synced and (first_time or reached_push_time):
                        all_successful = self.push_to_github()
                        if all_successful:
                            self.last_push_ms = ticks_ms()
                            self.last_push_stamp = localtime()
                            self.last_push_had_errors = False
                        else:
                            self.last_push_had_errors = True
                        self.wdt.feed()
                self.regular_update()
                for _ in range(10):  # actual wait loop between sensing temperature
                    self.sleep(1)
                    self.wdt.feed()
            except KeyboardInterrupt:  # pragma: no cover
                self.print("Encountered keyboard interrupt, exiting")
                return
            except Exception as e:
                self.print(str(e))
                self.show_fatal_error(e)
                for _ in range(30):
                    self.sleep(1)
                    self.wdt.feed()
            first_time = False
            if self.mode == OperatingMode.UnitTesting:
                break

    def print(self, message: str) -> None:
        if self.mode == OperatingMode.UnitTesting:
            self.printed_messages_for_testing += "\n" + message
        else:  # pragma: no cover
            print(message)

    def sleep(self, seconds: float) -> None:
        if self.mode != OperatingMode.UnitTesting:  # pragma: no cover
            from time import sleep
            sleep(seconds)

    # TODO: Add blink and infinite_loop functions to handle testing nicely

    # noinspection PyTypeHints
    def display_text(self, point: tuple[int, int], text: str, color: tuple, size: int):
        if self.mode == OperatingMode.UnitTesting:
            self.displayed_messages_for_testing += "\n" + text
        self.tft.text(point, text, color, FONT, size, nowrap=True)

    def display_dev_mode_warning(self):
        self.print("GP22 jumper is connected; device is in developer mode")
        self.tft.fill(Color.BLACK)
        self.display_text((7, 5), "*DEV MODE*", Color.YELLOW, 2)
        self.display_text((7, 25), "GP22 jumper active", Color.YELLOW, 1)
        self.display_text((7, 35), "In developer mode", Color.YELLOW, 1)
        self.tft.rect((15, 60), (50, 90), Color.WHITE)
        self.tft.fillrect((30, 50), (20, 20), Color.GRAY)
        self.tft.fillrect((27, 95), (26, 26), Color.WHITE)
        pins_to_print = ["GP27", "GP26", "RUN", "GP22", "GND", "GP21", "GP20", "GP19"]
        y = 65
        for pin in pins_to_print:
            self.display_text((70, y), pin, Color.YELLOW, 1)
            y += 10
        self.tft.hline((92, 88), 15, Color.YELLOW)
        self.tft.vline((107, 88), 11, Color.YELLOW)
        self.tft.hline((97, 98), 10, Color.YELLOW)

    def regular_update(self):
        self.tft.fill(Color.BLACK)
        # SENSOR INFORMATION
        self.tft.hline((0, 5), 24, Color.GRAY)
        self.tft.hline((0, 10), 24, Color.GRAY)
        self.tft.hline((106, 5), 24, Color.GRAY)
        self.tft.hline((106, 10), 24, Color.GRAY)
        self.display_text((27, 0), "Sensors", Color.WHITE, 2)
        # Need to alert here on the screen if the sensor data is bad
        y = 17
        for sensor in self.sensors:
            if sensor.active:
                self.display_text((0, y), f"{sensor.label} {sensor.name}", Color.WHITE, 1)
            else:
                self.display_text((0, y), f"{sensor.label} {sensor.name}", Color.YELLOW, 1)
            y += 10
            if sensor.temperature_f:
                temp_string = f"{sensor.temperature_f:.2f} F"
                self.display_text((27, y), temp_string, Color.WHITE, 2)
                if len(temp_string) == 6 or len(temp_string) == 7:
                    # draw the degree symbol if it's like "X.YY F" or "XX.YY F"
                    self.tft.circle((89, y + 3), 3, Color.WHITE)
            else:
                self.display_text((27, y), "NULL", Color.YELLOW, 1)
            y += 17
        # WI-FI INFORMATION
        self.tft.hline((0, 79), 40, Color.GRAY)
        self.tft.hline((0, 84), 40, Color.GRAY)
        self.tft.hline((88, 79), 40, Color.GRAY)
        self.tft.hline((88, 84), 40, Color.GRAY)
        self.display_text((44, 74), "WiFi", Color.WHITE, 2)
        if self.wlan.isconnected():
            self.display_text((0, 90), "Connected!", Color.GREEN, 1)
            self.display_text((0, 100), f"SSID: {self.ssid}", Color.WHITE, 1)
            self.display_text((0, 110), f"IP: {self.ip}", Color.WHITE, 1)
        else:
            self.display_text((0, 90), "****DISCONNECTED****", Color.RED, 1)
        # UPDATE INFORMATION
        self.tft.hline((0, 128), 24, Color.GRAY)
        self.tft.hline((0, 133), 24, Color.GRAY)
        self.tft.hline((106, 128), 24, Color.GRAY)
        self.tft.hline((106, 133), 24, Color.GRAY)
        self.display_text((27, 123), "Updates", Color.WHITE, 2)
        if self.last_temp_stamp:
            temp_time_text = "Read: {:02d}:{:02d}:{:02d} (UTC)".format(self.last_temp_stamp[3], self.last_temp_stamp[4],
                                                                       self.last_temp_stamp[5])
            self.display_text((0, 140), temp_time_text, Color.WHITE, 1)
        else:
            self.display_text((0, 140), "Read: NEVER", Color.YELLOW, 1)
        if self.last_push_had_errors:
            self.display_text((0, 150), "Last Push Had Errors", Color.RED, 1)
        elif self.last_push_stamp:
            github_time_text = "Push: {:02d}:{:02d}:{:02d} (UTC)".format(self.last_push_stamp[3],
                                                                         self.last_push_stamp[4],
                                                                         self.last_push_stamp[5])
            self.display_text((0, 150), github_time_text, Color.WHITE, 1)
        else:
            self.display_text((0, 150), "Push: NEVER", Color.YELLOW, 1)

    def show_fatal_error(self, error: Exception | str):
        self.tft.fill(Color.BLACK)
        self.display_text((0, 5), "*EXCEPTION*", Color.RED, 2)
        y = 25
        msg = str(error)
        self.print(msg)
        for i in range(0, len(msg), 20):
            self.display_text((0, y), (msg[i:i + 20]), Color.RED, 1)
            y += 10

    def try_to_connect_to_wifi(self) -> None:
        self.ssid = ""
        self.ip = ""
        wifi_connect_timeout_ms = 10_000
        available = {net[0].decode() for net in self.wlan.scan()}
        for ssid, pw in WIFI_NETWORKS:
            if ssid not in available:
                continue
            self.wlan.connect(ssid, pw)
            start = ticks_ms()
            while not self.wlan.isconnected():
                if self.mode == OperatingMode.UnitTesting:  # assuming it is just disabling Wi-Fi
                    break
                else:  # pragma: no cover
                    if ticks_diff(ticks_ms(), start) > wifi_connect_timeout_ms:
                        break
                    self.sleep(0.2)
                    self.wdt.feed()
            if self.wlan.isconnected():
                self.ip, _, _, _ = self.wlan.ifconfig()
                self.ssid = self.wlan.config('ssid')
                break

    def update_temperatures(self):
        if not self.sensors:
            return
        try:
            self.ds.convert_temp()
        except OneWireError:  # no need to capture the variable, the string seems to be empty
            raise Exception("Could not convert_temp, check connections carefully!") from None
        self.sleep(0.75)  # wait 750ms after calling convert_temp and before sampling temps
        for sensor in self.sensors:
            try:
                temperature_c = self.ds.read_temp(sensor.rom)
                sensor.temperature_f = (temperature_c * 9.0 / 5.0) + 32.0
            except Exception as e:
                raise Exception(f"Could not get temperature from sensor named {sensor.name}") from e

    def try_to_sync_time(self, timeout=3):
        s = socket(AF_INET, SOCK_DGRAM)
        # noinspection PyBroadException
        try:
            addr = getaddrinfo("pool.ntp.org", 123)[0][-1]
            s.settimeout(timeout)
            s.sendto(b'\x1b' + 47 * b'\0', addr)
            data, _ = s.recvfrom(48)
            t = unpack("!I", data[40:44])[0] - 2208988800  # magic number is 1970 offset
            tm = localtime(t)
            RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            self.time_synced = True
        except Exception:  # I'm not sure what all could happen
            pass  # just allow it to continue, unsynced for now
        finally:
            s.close()

    def try_to_get_sensor_details(self):
        # TODO: Make this versioned/tagged
        url = 'https://raw.githubusercontent.com/okielife/TempSensors/refs/heads/gh-pages/_data/config.json'
        # noinspection PyBroadException
        try:
            response = get(url)
            if response.status_code in (200, 201):
                data = load_json(response.raw)
                for sensor in self.sensors:
                    sensor.label = data['rom_hex_to_cable_number'][sensor.rom.hex()]
                    if sensor.label in data['sensors']:
                        sensor.name = data['sensors'][sensor.label]['short_name']
                        sensor.active = True
                    else:
                        sensor.name = "INACTIVE SENSOR"
                        sensor.active = False
                self.retrieved_sensor_info = True
            else:
                self.print(f"HTTP Error while trying to get sensor config: {response.status_code}")
            response.close()
        except Exception as e:
            print(e)
            pass  # just allow it to continue, sensors will be unnamed for now

    def push_to_github(self) -> bool:
        # we will return true if all were successful, but if any fail, it's fine,
        # because the unresponsive sensor check will alert us
        all_success = True
        t = localtime()
        current = f"{t[0]}-{t[1]:02d}-{t[2]:02d}-{t[3]:02d}-{t[4]:02d}-{t[5]:02d}"
        for sensor in self.sensors:
            file_content = f"""---
sensor_id: {sensor.rom.hex()}
sensor_name: {sensor.name}
temperature: {sensor.temperature_f}
measurement_time: {current}
---
{{}}
"""
            sensor_name_cleaned = sensor.name.replace(" ", "_")
            file_name = f"{current}_{sensor.rom.hex()}_{sensor_name_cleaned}.html"
            file_path = f"_posts/{sensor.rom.hex()}/{file_name}"
            url = f"https://api.github.com/repos/okielife/TempSensors/contents/{file_path}"
            headers = {'Accept': 'application/vnd.github + json', 'User-Agent': 'Temp Sensor',
                       'Authorization': f'Token {GITHUB_TOKEN}'}
            encoded_content = b2a_base64(file_content.encode()).decode()
            data = {'message': f"Updating {file_path}", 'content': encoded_content, 'branch': 'gh-pages'}
            try:
                response = put(url, headers=headers, json=data)
                if response.status_code not in (200, 201):
                    self.print(f"PUT Error: {response.text}")
                    all_success = False
            except (RuntimeError, OSError) as e:
                self.print(f"Could not send request, reason={e}, skipping this report, checks will continue")
                all_success = False
        return all_success

    def flash_led(self, num_times: int) -> None:
        self.led.off()
        for i in range(num_times * 2):
            self.sleep(0.2)
            self.led.toggle()
        self.led.off()


if __name__ == "__main__":  # pragma: no cover
    # we are launching this file manually from Thonny - do not create the watchdog
    from st7735 import TFT

    r = SensorBox(TFT, OperatingMode.DebugHardware)
    r.run()
