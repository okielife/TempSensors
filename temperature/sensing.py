# these imports are fine whether we are running on regular Python or MicroPython
from binascii import b2a_base64
from socket import getaddrinfo, socket, AF_INET, SOCK_DGRAM
from struct import unpack


# I'm not convinced I need the `from temperatures.` part, but it's ok for now
# TODO: Pass in the wifi networks, connected sensors, github token as args to the sensor box
try:  # pragma: no cover
    from board_base import BoardBase
    from screen_base import ScreenBase
    from config import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN
except ImportError:
    from temperature.board_base import BoardBase
    from temperature.screen_base import ScreenBase
    from temperature.config_template import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN


__version__ = 3
__revision__ = 7


class Sensor:
    def __init__(self, rom: bytes, label: str):
        self.rom = rom
        self.temperature_f = None
        self.label = label
        self.name = "UNKNOWN_NAME"
        self.active = False


class SensorBox:

    # noinspection PyPep8Naming
    def __init__(self, screen: ScreenBase, board: BoardBase):
        # Unfortunately, this SensorBox will be acting different based on the current scenario
        # I will try to keep that to a minimum to avoid complexity in here. But there will likely
        # be a few cases that I want to handle different.  For example, I do not want to accumulate
        # the printed messages when running normally, or we would hit memory issues.  So only
        # accumulate those when unit testing.
        self.screen = screen
        self.board = board

        # basic member variables
        self.last_temp_stamp = None
        self.last_push_stamp = None
        self.last_push_had_errors = False
        self.last_push_ms = 0
        self.time_synced = False
        self.retrieved_sensor_info = False

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
        self.screen.text((15, post_y_starting), "STARTING", self.screen.GREEN, 2)
        self.screen.text((0, post_y_version), f"Version {__version__}.{__revision__}", self.screen.WHITE, 2)
        self.screen.text((0, post_y_screen), "Screen:  OK", self.screen.WHITE, 2)
        self.board.feed_watchdog()

        # set up the sensors now
        scanned_roms = {rom.hex(): rom for rom in self.board.ds18x20_scan()}
        self.board.feed_watchdog()
        missing = [label for label, hex_id in CONNECTED_SENSORS if hex_id not in scanned_roms]
        if missing:
            self.show_fatal_error(f"Could not initialize sensor(s): {', '.join(missing)}; check connections")
            # just hang here forever, we don't want to continue without the sensors
            self.board.system_hang()
        self.sensors = [Sensor(scanned_roms[hex_id], label) for label, hex_id in CONNECTED_SENSORS]
        self.screen.text((0, post_y_sensors), "Sensors: OK", self.screen.WHITE, 2)
        self.board.feed_watchdog()

        # init the Wi-Fi and try to sync the clock

        self.board.active(True)
        self.ip = ""
        self.ssid = ""
        if not self.board.isconnected():
            self.try_to_connect_to_wifi()
        if self.board.isconnected():
            self.ip, _, _, _ = self.board.ifconfig()
            self.ssid = self.board.config('ssid')
            self.screen.text((0, post_y_wifi), "Wi-Fi:   OK", self.screen.WHITE, 2)
            self.try_to_sync_time()
            if self.time_synced:
                t = self.board.localtime()
                self.screen.text((0, post_y_clock), "Clock:   OK", self.screen.WHITE, 2)
                self.screen.text((0, post_y_date), "Date: {:02d}/{:02d}".format(t[1], t[2]), self.screen.WHITE, 2)
            else:
                self.show_fatal_error("CLOCK SYNC ERROR, will continue to boot in 5 seconds and retry sync later.")
                self.board.sleep(5)
            self.try_to_get_sensor_details()
            if self.retrieved_sensor_info:
                self.screen.text((0, post_y_config), "Config:  OK", self.screen.WHITE, 2)
            else:
                self.screen.text((0, post_y_config), "Config: ERR", self.screen.RED, 2)
                self.show_fatal_error(
                    "Could not retrieve sensor config data from GitHub, "
                    "will continue to boot in 5 seconds and retry later."
                )
                self.board.sleep(5)
        else:
            self.screen.text((0, post_y_wifi), "Wi-Fi:  NOT", self.screen.YELLOW, 2)
            self.screen.text((0, post_y_clock), "READY, CHECK", self.screen.YELLOW, 2)
            self.screen.text((0, post_y_date), "NETWORK", self.screen.YELLOW, 2)
            self.screen.text((0, post_y_config), "WILL RETRY", self.screen.YELLOW, 2)
            self.board.sleep(2)
        self.board.feed_watchdog()

        self.screen.text((0, post_y_booting), "BOOTING UP!", self.screen.WHITE, 2)
        self.board.feed_watchdog()

    def run(self):
        github_push_interval_ms = 3_600_000
        self.board.feed_watchdog()
        first_time = True
        while True:
            try:
                self.update_temperatures()
                self.board.feed_watchdog()
                self.last_temp_stamp = self.board.localtime()
                if not self.board.isconnected():
                    # try to connect, but if we can't, just continue to updating temps and looping
                    self.try_to_connect_to_wifi()
                    self.board.feed_watchdog()
                if self.board.isconnected():
                    if not self.time_synced:
                        self.try_to_sync_time()
                        self.board.feed_watchdog()
                    if not self.retrieved_sensor_info:
                        self.try_to_get_sensor_details()
                    # we don't necessarily need the sensor extra info to push to GitHub,
                    # so no need to check if self.retrieved_sensor_info
                    interval = self.board.ticks_diff(self.board.ticks_ms(), self.last_push_ms)
                    reached_push_time = interval > github_push_interval_ms
                    if self.time_synced and (first_time or reached_push_time):
                        all_successful = self.push_to_github()
                        if all_successful:
                            self.last_push_ms = self.board.ticks_ms()
                            self.last_push_stamp = self.board.localtime()
                            self.last_push_had_errors = False
                        else:
                            self.last_push_had_errors = True
                        self.board.feed_watchdog()
                self.regular_update()
                for _ in range(10):  # actual wait loop between sensing temperature
                    self.board.sleep(1)
                    self.board.feed_watchdog()
            except KeyboardInterrupt:  # pragma: no cover
                self.board.print("Encountered keyboard interrupt, exiting")
                return
            except Exception as e:
                self.board.print(str(e))
                self.show_fatal_error(e)
                for _ in range(30):
                    self.board.sleep(1)
                    self.board.feed_watchdog()
            first_time = False
            if self.board.run_forever():
                continue
            else:
                break

    def display_dev_mode_warning(self):
        self.board.print("GP22 jumper is connected; device is in developer mode")
        self.screen.fill(self.screen.BLACK)
        self.screen.text((7, 5), "*DEV MODE*", self.screen.YELLOW, 2)
        self.screen.text((7, 25), "GP22 jumper active", self.screen.YELLOW, 1)
        self.screen.text((7, 35), "In developer mode", self.screen.YELLOW, 1)
        self.screen.rect((15, 60), (50, 90), self.screen.WHITE)
        self.screen.fillrect((30, 50), (20, 20), self.screen.GRAY)
        self.screen.fillrect((27, 95), (26, 26), self.screen.WHITE)
        pins_to_print = ["GP27", "GP26", "RUN", "GP22", "GND", "GP21", "GP20", "GP19"]
        y = 65
        for pin in pins_to_print:
            self.screen.text((70, y), pin, self.screen.YELLOW, 1)
            y += 10
        self.screen.hline((92, 88), 15, self.screen.YELLOW)
        self.screen.vline((107, 88), 11, self.screen.YELLOW)
        self.screen.hline((97, 98), 10, self.screen.YELLOW)

    def regular_update(self):
        self.screen.fill(self.screen.BLACK)
        # SENSOR INFORMATION
        self.screen.hline((0, 5), 24, self.screen.GRAY)
        self.screen.hline((0, 10), 24, self.screen.GRAY)
        self.screen.hline((106, 5), 24, self.screen.GRAY)
        self.screen.hline((106, 10), 24, self.screen.GRAY)
        self.screen.text((27, 0), "Sensors", self.screen.WHITE, 2)
        # Need to alert here on the screen if the sensor data is bad
        y = 17
        for sensor in self.sensors:
            if sensor.active:
                self.screen.text((0, y), f"{sensor.label} {sensor.name}", self.screen.WHITE, 1)
            else:
                self.screen.text((0, y), f"{sensor.label} {sensor.name}", self.screen.YELLOW, 1)
            y += 10
            if sensor.temperature_f:
                temp_string = f"{sensor.temperature_f:.2f} F"
                self.screen.text((27, y), temp_string, self.screen.WHITE, 2)
                if len(temp_string) == 6 or len(temp_string) == 7:
                    # draw the degree symbol if it's like "X.YY F" or "XX.YY F"
                    self.screen.circle((89, y + 3), 3, self.screen.WHITE)
            else:
                self.screen.text((27, y), "NULL", self.screen.YELLOW, 1)
            y += 17
        # WI-FI INFORMATION
        self.screen.hline((0, 79), 40, self.screen.GRAY)
        self.screen.hline((0, 84), 40, self.screen.GRAY)
        self.screen.hline((88, 79), 40, self.screen.GRAY)
        self.screen.hline((88, 84), 40, self.screen.GRAY)
        self.screen.text((44, 74), "WiFi", self.screen.WHITE, 2)
        if self.board.isconnected():
            self.screen.text((0, 90), "Connected!", self.screen.GREEN, 1)
            self.screen.text((0, 100), f"SSID: {self.ssid}", self.screen.WHITE, 1)
            self.screen.text((0, 110), f"IP: {self.ip}", self.screen.WHITE, 1)
        else:
            self.screen.text((0, 90), "****DISCONNECTED****", self.screen.RED, 1)
        # UPDATE INFORMATION
        self.screen.hline((0, 128), 24, self.screen.GRAY)
        self.screen.hline((0, 133), 24, self.screen.GRAY)
        self.screen.hline((106, 128), 24, self.screen.GRAY)
        self.screen.hline((106, 133), 24, self.screen.GRAY)
        self.screen.text((27, 123), "Updates", self.screen.WHITE, 2)
        if self.last_temp_stamp:
            temp_time_text = "Read: {:02d}:{:02d}:{:02d} (UTC)".format(self.last_temp_stamp[3], self.last_temp_stamp[4],
                                                                       self.last_temp_stamp[5])
            self.screen.text((0, 140), temp_time_text, self.screen.WHITE, 1)
        else:
            self.screen.text((0, 140), "Read: NEVER", self.screen.YELLOW, 1)
        if self.last_push_had_errors:
            self.screen.text((0, 150), "Last Push Had Errors", self.screen.RED, 1)
        elif self.last_push_stamp:
            github_time_text = "Push: {:02d}:{:02d}:{:02d} (UTC)".format(self.last_push_stamp[3],
                                                                         self.last_push_stamp[4],
                                                                         self.last_push_stamp[5])
            self.screen.text((0, 150), github_time_text, self.screen.WHITE, 1)
        else:
            self.screen.text((0, 150), "Push: NEVER", self.screen.YELLOW, 1)

    def show_fatal_error(self, error: Exception | str):
        self.screen.fill(self.screen.BLACK)
        self.screen.text((0, 5), "*EXCEPTION*", self.screen.RED, 2)
        y = 25
        msg = str(error)
        self.board.print(msg)
        for i in range(0, len(msg), 20):
            self.screen.text((0, y), (msg[i:i + 20]), self.screen.RED, 1)
            y += 10

    def try_to_connect_to_wifi(self) -> None:
        self.ssid = ""
        self.ip = ""
        wifi_connect_timeout_ms = 10_000
        available = {n[0].decode() for n in self.board.scan()}
        for ssid, pw in WIFI_NETWORKS:
            if ssid not in available:
                continue
            self.board.connect(ssid, pw)
            start = self.board.ticks_ms()
            while not self.board.isconnected():
                if self.board.ticks_diff(self.board.ticks_ms(), start) > wifi_connect_timeout_ms:
                    break
                self.board.sleep(0.2)
                self.board.feed_watchdog()
            if self.board.isconnected():
                self.ip, _, _, _ = self.board.ifconfig()
                self.ssid = self.board.config('ssid')
                break

    def update_temperatures(self):
        if not self.sensors:
            return
        try:
            self.board.ds18x20_convert_temp()
        except Exception:  # no need to capture the variable, the string seems to be empty
            raise Exception("Could not convert_temp, check connections carefully!") from None
        self.board.sleep(0.75)  # wait 750ms after calling convert_temp and before sampling temps
        for sensor in self.sensors:
            try:
                temperature_c = self.board.ds18x20_read_temp(sensor.rom)
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
            tm = self.board.localtime(t)
            self.board.rtc_datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            self.time_synced = True
        except Exception:  # I'm not sure what all could happen
            pass  # just allow it to continue, unsynced for now
        finally:
            s.close()

    def try_to_get_sensor_details(self):
        # TODO: Make this versioned/tagged
        # something like:
        # https://raw.githubusercontent.com/okielife/TempSensors/9415cce73d7304f120dae78d9b60993843035ba0/_data/config.json  # noqa: E501
        url = 'https://raw.githubusercontent.com/okielife/TempSensors/refs/heads/gh-pages/_data/config.json'
        # noinspection PyBroadException
        try:
            response = self.board.http_get(url)
            if response.status_code in (200, 201):
                data = self.board.load_json(response.raw)
                for sensor in self.sensors:
                    sensor.label = data['rom_hex_to_cable_number'][sensor.rom.hex()]
                    if sensor.label in data['sensors']:
                        sensor.name = data['sensors'][sensor.label]['short_name']
                        sensor.active = data['sensors'][sensor.label].get('active', False)
                    else:
                        sensor.name = "INACTIVE SENSOR"
                        sensor.active = False
                self.retrieved_sensor_info = True
            else:
                self.board.print(f"HTTP Error while trying to get sensor config: {response.status_code}")
            response.close()
        except Exception as e:
            self.board.print(str(e))
            pass  # just allow it to continue, sensors will be unnamed for now

    def push_to_github(self) -> bool:
        # we will return true if all were successful, but if any fail, it's fine,
        # because the unresponsive sensor check will alert us
        all_success = True
        t = self.board.localtime()
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
                response = self.board.http_put(url, headers=headers, json=data)
                if response.status_code not in (200, 201):
                    self.board.print(f"PUT Error: {response.text}")
                    all_success = False
            except (RuntimeError, OSError) as e:
                self.board.print(f"Could not send request, reason={e}, skipping this report, checks will continue")
                all_success = False
        return all_success

    def flash_led(self, num_times: int) -> None:
        self.board.led().off()
        for i in range(num_times * 2):
            self.board.sleep(0.2)
            self.board.led().toggle()
        self.board.led().off()


if __name__ == "__main__":  # pragma: no cover
    # this entry point should only ever be called from Micropython hardware itself
    # we are launching this file manually from Thonny - do not create the watchdog
    from screen_tft import ScreenTFT
    from board_mock import BoardMock
    tft = ScreenTFT.default_construct()
    net = BoardMock()
    r = SensorBox(tft, net)
    r.run()
