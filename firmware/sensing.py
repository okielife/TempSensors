from binascii import b2a_base64

from firmware.board_base import BoardBase
from firmware.screen_base import ScreenBase
from firmware.config_base import ConfigBase

__version__ = 3
__revision__ = 7


class Sensor:
    def __init__(self, rom: bytes):
        self.rom = rom
        self.label = "??"
        self.temperature_f: float = -1000
        self.name = "UNKNOWN_NAME"
        self.active = False


class SensorBox:

    # noinspection PyPep8Naming
    def __init__(self, board: BoardBase, screen: ScreenBase, config: ConfigBase):
        """
        This constructor sets up local copies of the screen, board, and other config variables passed in.
        The constructor then initializes member variables and finally calls post() to boot up.

        :param board: A board instance for hardware API, should inherit BoardBase, could be BoardPico, BoardMOck, etc.
        :param screen: A screen instance for display API, should inherit ScreenBase, could be ScreenTFT, ScreenTk, etc.
        :param config: A config instance which will provide GitHub token and Wi-Fi network information
        """
        # Unfortunately, this SensorBox will be acting different based on the current scenario
        # I will try to keep that to a minimum to avoid complexity in here. But there will likely
        # be a few cases that I want to handle different.  For example, I do not want to accumulate
        # the printed messages when running normally, or we would hit memory issues.  So only
        # accumulate those when unit testing.
        self.board = board
        self.screen = screen
        self.config = config
        self.config.establish_config(self.screen)
        self.wifi_networks = self.config.wifi_networks()
        self.github_token = self.config.github_token()

        # basic member variables
        self.last_temp_stamp: tuple = ()
        self.last_push_stamp: tuple = ()
        self.last_push_had_errors = False
        self.last_push_ms = 0
        self.time_synced = False
        self.retrieved_sensor_info = False
        self.developer_mode = False
        self.ip = ""
        self.ssid = ""
        self.sensors: list[Sensor] = list()

        # always try to make the watchdog, the board setup will decide whether to actually do it.  Then POST
        self.board.create_watchdog(8000)
        self.post()

    def post(self) -> None:
        """
        This functions performs the boot process, kind of mocking a POST step.
        There are some failure conditions which will cause the boot to hang indefinitely.
        There are also some conditions which will cause the boot to pause, then continue, leaving setup incomplete.
        Basic flow is:
        - Report the version and screen status.
        - Check connected sensor ROMs and make sure they can be properly initialized, if not then HANG FOREVER.
        - If not already connected to Wi-Fi, try to connect -- this will only try for a few seconds before giving up.
        - Gather Wi-Fi details, but If still not connected, we can't do anything else, so report no Wi-Fi and leave.
        - Try to sync the clock from the network -- this will only try for a few seconds before giving up.
        - Try to get the sensor details from the centralized dashboard config file.
        """
        y_starting = 0
        y_version = 18
        y_screen = 36
        y_sensors = 54
        y_wifi = 72
        y_clock = 90
        y_date = 108
        y_config = 126
        y_booting = 144

        self.screen.fill(self.screen.BLACK)
        self.screen.text((15, y_starting), "STARTING", self.screen.GREEN, 2)
        self.screen.text((0, y_version), f"Version {__version__}.{__revision__}", self.screen.WHITE, 2)
        self.screen.text((0, y_screen), "Screen:   ", self.screen.WHITE, 2)
        self.screen.text((88, y_screen), "R", self.screen.RED, 2)
        self.screen.text((101, y_screen), "G", self.screen.GREEN, 2)
        self.screen.text((114, y_screen), "B", self.screen.BLUE, 2)
        self.board.feed_watchdog()

        # set up the sensors now
        self.sensors = [Sensor(rom) for rom in self.board.ds18x20_scan()]
        self.screen.text((0, y_sensors), f"Sensors:  {len(self.sensors)}", self.screen.WHITE, 2)
        self.board.feed_watchdog()

        # init the Wi-Fi and try to connect as needed
        self.board.active(True)
        if not self.board.isconnected():
            self.try_to_connect_to_wifi()

        # get Wi-Fi details, but if we still aren't connected, there isn't much we can do, just report and leave
        if self.board.isconnected():
            self.ip, _, _, _ = self.board.ifconfig()
            self.ssid = self.board.config('ssid')
            self.screen.text((0, y_wifi), "Wi-Fi:   OK", self.screen.WHITE, 2)
        else:
            self.screen.text((0, y_wifi), "Wi-Fi:  NOT", self.screen.YELLOW, 2)
            self.screen.text((0, y_clock), "READY, CHECK", self.screen.YELLOW, 2)
            self.screen.text((0, y_date), "NETWORK", self.screen.YELLOW, 2)
            self.screen.text((0, y_config), "WILL RETRY", self.screen.YELLOW, 2)
            self.screen.text((0, y_booting), "BOOTING UP!", self.screen.WHITE, 2)
            self.board.sleep(2)
            self.board.feed_watchdog()
            return

        # try to sync the clock
        self.try_to_sync_time()
        if self.time_synced:
            t = self.board.localtime()
            self.screen.text((0, y_clock), "Clock:   OK", self.screen.WHITE, 2)
            self.screen.text((0, y_date), "Date: {:02d}/{:02d}".format(t[1], t[2]), self.screen.WHITE, 2)
        else:
            self.show_fatal_error("CLOCK SYNC ERROR, will continue to boot in 5 seconds and retry sync later.")
            self.board.sleep(5)
            self.screen.fill(self.screen.BLACK)

        # try to get sensor details
        self.try_to_get_sensor_details()
        if self.retrieved_sensor_info:
            self.screen.text((0, y_config), "Config:  OK", self.screen.WHITE, 2)
        else:
            self.screen.text((0, y_config), "Config: ERR", self.screen.RED, 2)
            self.show_fatal_error(
                "Could not retrieve sensor config data from GitHub, "
                "will continue to boot in 5 seconds and retry later."
            )
            self.board.sleep(5)

        # final report and leave
        self.screen.text((0, y_booting), "BOOTING UP!", self.screen.WHITE, 2)
        self.board.sleep(3)
        self.board.feed_watchdog()

    def run(self) -> None:
        """
        This function performs the "infinite" loop of actually running the sensor.
        Some of the logic is just like the post function, where it is continually checking what has been completed.
        This function is small to keep a clear and obvious understanding of what is required on a typical iteration.
        In summary, this has an infinite loop, where each loop performs sensing, network, GitHub, display, and idling.
        This function will trap all exceptions - keyboard interrupts lead to a graceful exit, all others will return.
        In development, this will result in a reset() call to reboot the pico and restart everything.
        """
        if self.board.developer_mode():
            self.board.print("GP14 jumper is connected; device is in developer mode")
            self.enter_dev_mode()
            self.board.system_hang()
        self.board.feed_watchdog()
        first_time = True
        while True:
            try:
                self.phase_sensing()
                self.phase_network()
                self.phase_push(first_time)
                self.update_display()
                self.phase_idle()
            except KeyboardInterrupt:  # pragma: no cover
                self.board.print("Encountered keyboard interrupt, exiting")
                return
            except Exception as e:
                self.phase_error(e)
                return
            first_time = False
            if not self.board.run_forever():
                break

    def phase_sensing(self) -> None:
        """
        "Sensing" run phase which is basically just reading new temperatures and logging the current time
        """
        self.update_temperatures()
        self.board.feed_watchdog()
        self.last_temp_stamp = self.board.localtime()

    def phase_network(self) -> None:
        """
        "Network" run phase which is basically just trying to connect to Wi-Fi again, and once connected, trying to
        sync time and do an http request for active sensor info.
        """
        if not self.board.isconnected():
            self.try_to_connect_to_wifi()
            self.board.feed_watchdog()
        if not self.board.isconnected():
            return
        if not self.time_synced:
            self.try_to_sync_time()
            self.board.feed_watchdog()
        if not self.retrieved_sensor_info:
            self.try_to_get_sensor_details()

    def phase_push(self, first_time: bool) -> None:
        """
        "Push" run phase, which is basically waiting until connected and enough time has passed, then pushing data
        up to GitHub, and logging the time.
        """
        if not self.board.isconnected():
            return
        if not self.time_synced:
            return
        interval = self.board.ticks_diff(self.board.ticks_ms(), self.last_push_ms)
        github_push_interval_ms = 3_600_000
        reached_push_time = interval > github_push_interval_ms
        if not (first_time or reached_push_time):
            return
        success = self.push_to_github()
        if success:
            self.last_push_ms = self.board.ticks_ms()
            self.last_push_stamp = self.board.localtime()
            self.last_push_had_errors = False
        else:
            self.last_push_had_errors = True
        self.board.feed_watchdog()

    def phase_idle(self) -> None:
        """
        "Idle" run phase, which is basically just sleep for a little while between sensing loops
        """
        for _ in range(10):  # actual wait loop between sensing temperature
            self.board.sleep(1)
            self.board.feed_watchdog()

    def phase_error(self, e: Exception) -> None:
        """
        "Error" run phase, which is just the generalized error reporter, including a sleep to hold it on the screen.
        """
        self.board.print(str(e))
        self.show_fatal_error(str(e))
        self.board.sleep(30)

    def update_display(self) -> None:
        """
        This function does a normal update of the screen, gathering data and presenting on whatever screen is registered
        """
        self.screen.fill(self.screen.BLACK)
        # SENSOR INFORMATION
        self.screen.text((33, 2), f"Sensors {__version__}.{__revision__}", self.screen.GREEN, 1)
        self.screen.hline((0, 10), 128, self.screen.GRAY)
        # Need to alert here on the screen if the sensor data is bad
        y = 14
        for sensor in self.sensors:
            if sensor.active:
                self.screen.text((0, y), f"{sensor.label} {sensor.name}", self.screen.WHITE, 1)
            else:
                self.screen.text((0, y), f"{sensor.label} {sensor.name}", self.screen.YELLOW, 1)
            y += 10
            temp_string = f"{sensor.temperature_f:.2f} F"
            self.screen.text((27, y), temp_string, self.screen.WHITE, 2)
            # draw the degree symbol if it's like "X.YY F" or "XX.YY F"
            if len(temp_string) == 6:
                self.screen.circle((78, y + 3), 3, self.screen.WHITE)
            elif len(temp_string) == 7:
                self.screen.circle((90, y + 3), 3, self.screen.WHITE)
            elif len(temp_string) == 8:
                self.screen.circle((102, y + 3), 3, self.screen.WHITE)
            y += 19
        # WI-FI INFORMATION
        self.screen.hline((0, 78), 40, self.screen.GRAY)
        self.screen.hline((0, 83), 40, self.screen.GRAY)
        self.screen.hline((88, 78), 40, self.screen.GRAY)
        self.screen.hline((88, 83), 40, self.screen.GRAY)
        self.screen.text((44, 73), "WiFi", self.screen.WHITE, 2)
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

    def enter_dev_mode(self) -> None:
        """
        This function displays the developer screen as a signal (mostly a reminder) that the debug jumper is connected
        """
        # TODO: Fix this display, also maybe move it to the board class itself or the screen class??
        self.developer_mode = True
        self.screen.fill(self.screen.BLACK)
        self.screen.text((7, 5), "*DEV MODE*", self.screen.YELLOW, 2)
        self.screen.text((7, 25), "GP22 jumper active", self.screen.YELLOW, 1)
        self.screen.text((7, 35), "In developer mode", self.screen.YELLOW, 1)
        self.screen.rect((60, 60), (50, 90), self.screen.WHITE)
        self.screen.fillrect((75, 50), (20, 20), self.screen.GRAY)
        self.screen.fillrect((72, 95), (26, 26), self.screen.WHITE)
        pins_to_print = reversed(["GP15", "GP14", " GND", "GP13", "GP12", "GP11", "GP10", " GND"])
        y = 65
        for pin in pins_to_print:
            self.screen.text((30, y), pin, self.screen.YELLOW, 1)
            y += 10
        self.screen.hline((12, 118), 18, self.screen.YELLOW)
        self.screen.vline((12, 118), 10, self.screen.YELLOW)
        self.screen.hline((12, 128), 11, self.screen.YELLOW)

    def show_fatal_error(self, error: str) -> None:
        """
        This function is responsible for issuing a fatal message to the user.  This includes printing the message
        according to the board instance's print capability, as well as attempting to break up the message and display
        it on the screen.
        """
        self.screen.fill(self.screen.BLACK)
        self.screen.text((0, 5), "*EXCEPTION*", self.screen.RED, 2)
        y = 25
        msg = str(error)
        self.board.print(msg)
        for i in range(0, len(msg), 20):
            self.screen.text((0, y), (msg[i:i + 20]), self.screen.RED, 1)
            y += 10

    def try_to_connect_to_wifi(self) -> None:
        """
        This function tries to connect the device to Wi-Fi.
        It first resets the known ssid/ip, loops over known Wi-Fi data, connects up to a given timeout interval,
        and either succeeds or ultimately just gives up and leaves it disconnected.
        """
        self.ssid = ""
        self.ip = ""
        wifi_connect_timeout_ms = 10_000
        available = {n[0].decode() for n in self.board.scan()}
        for ssid, pw in self.wifi_networks.items():
            if ssid not in available:
                continue
            self.board.connect(ssid, pw)
            start = self.board.ticks_ms()
            while not self.board.isconnected():
                if self.board.ticks_diff(self.board.ticks_ms(), start) > wifi_connect_timeout_ms:
                    break
                # during unit testing, I'm not trying to reach these lines
                # I don't want to have to make ticks_diff actually increment forward some amount of time
                # within this loop.  I'm satisfied that in real hardware, it will sleep until the time
                # ticks forward enough and eventually give up.
                self.board.sleep(0.2)  # pragma: no cover
                self.board.feed_watchdog()  # pragma: no cover
            if self.board.isconnected():
                self.ip, _, _, _ = self.board.ifconfig()
                self.ssid = self.board.config('ssid')
                break

    def update_temperatures(self) -> None:
        """
        This function is responsible for updating the sensed temperature values on all connected sensors.
        The process is pretty simple, just call to convert_temp on the sensors, which resets the sensor scratchpad,
        sends a signal to read "all" sensors, and then actually converts the live reading from the sensor into a
        meaningful temperature.  This is why you need to call this with each pass, since that convert_temp call
        is actually what updates the temperatures on the sensor's scratchpad.  Once the temperature is there, we simply
        update the Sensor wrapper instance with the new temperature and move on.
        """
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

    def try_to_sync_time(self) -> None:
        """
        This function tries to synchronize the clock (RTC) using an NTP server response.
        The UDP packet is prepared, sent, the response is parsed into a Unix time, and stored back on the board clock.
        If any failures arise, this function just returns, leaving the time un-synchronized, so that it will try again.
        """
        t = self.board.get_ntp_timestamp()
        if t is None:
            return
        else:
            tm = self.board.localtime(t)
            try:
                self.board.rtc_datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            except OSError:
                return
            self.time_synced = True

    def try_to_get_sensor_details(self) -> None:
        """
        This function is responsible for trying to download and parse the sensor configuration from the centralized
        JSON config on the dashboard repo.  The config file should be a static URL so that we don't have to get back
        on the sensor box code to update the location.
        The function is pretty standard - just go to the prescribed URL, parse the JSON sensor data, and then update
        the local array of Sensor information.
        """
        url = 'https://raw.githubusercontent.com/okielife/TempSensors/main/dashboard/_data/config.json'
        response = None
        try:
            response = self.board.http_get(url)
            if response.status_code not in (200, 201):
                self.board.print(f"HTTP Error while trying to get sensor config: {response.status_code}")
                return
            data = self.board.load_json(response.raw)
            any_issues = False
            for sensor in self.sensors:
                rom_hex = sensor.rom.hex()
                label = data.get('rom_hex_to_cable_number', {}).get(rom_hex)
                sensor.label = label
                if not label:
                    sensor.name = "UNKNOWN SENSOR"
                    sensor.active = False
                    any_issues = True
                    continue
                if label in data['sensors']:
                    sensor.name = data['sensors'][label].get('short_name', '???')
                    sensor.active = data['sensors'][label].get('active', False)
                else:
                    sensor.name = "UNKNOWN SENSOR"
                    sensor.active = False
                    any_issues = True
            if not any_issues:
                self.retrieved_sensor_info = True
        except Exception as e:
            self.board.print(str(e))  # print, but just allow it to continue, sensors will be unnamed for now
        finally:
            if response:
                response.close()

    def push_to_github(self) -> bool:
        """
        This function is responsible for pushing updated temperature results to GitHub for all connected sensors.
        The content is a simple YAML file header with a few variables at the top and no body HTML content beneath ---.
        The push is actually a "put" http action where it will live at the repo's gh-pages branch at:
        /_posts/romHexAbc123Def/2026-02-24-10-30-02_romHexAbc123Def_Sensor_Name_Here.html.
        If any fail, it will return False, and the sensor box can alert that the last push failed.
        Also, if this keeps failing for any reason, the periodic sensor responsiveness check will alert us.
        :return bool: True if successful, False otherwise
        """
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
            file_path = f"data/{sensor.rom.hex()}/{file_name}"
            url = f"https://api.github.com/repos/okielife/TempSensors/contents/{file_path}"
            headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Temp Sensor',
                       'Authorization': f'Token {self.github_token}'}
            encoded_content = b2a_base64(file_content.encode()).decode().strip()
            data = {'message': f"Updating {file_path}", 'content': encoded_content, 'branch': 'sensor_data'}
            try:
                response = self.board.http_put(url, headers=headers, json=data)
                if response.status_code not in (200, 201):
                    self.board.print(f"PUT Error: {response.text}")
                    all_success = False
            except Exception as e:
                self.board.print(f"Could not send request, reason={e}, skipping this report, checks will continue")
                all_success = False
        return all_success


if __name__ == "__main__":  # pragma: no cover
    # this entry point should only ever be called from Micropython hardware itself
    # we are launching this file manually from Thonny - do not create the watchdog
    from firmware.screen_tft import ScreenTFT
    from firmware.board_pico import BoardPico
    from firmware.config_pico import ConfigPico

    tft = ScreenTFT()
    pico = BoardPico()
    c = ConfigPico()
    r = SensorBox(pico, tft, c)
    r.run()
