from time import time
from unittest import TestCase

from firmware.board_mock import BoardMock
from firmware.screen_mock import ScreenMock
from firmware.sensing import SensorBox
from firmware.config_mock import ConfigMock


class TestSensing(TestCase):

    def setUp(self) -> None:
        self.screen = ScreenMock()
        self.config = ConfigMock()
        self.config.networks = {"WiFiNetworkOne": "Password", "AlphaHotSpot": "OK"}
        self.board = BoardMock()

    def test_construction(self) -> None:
        """Given the inputs we have set up to mock, we would expect it to be connected and set up"""
        s = SensorBox(self.board, self.screen, self.config)
        self.assertTrue(len(s.sensors) == 2)
        self.assertTrue(s.board.isconnected())
        self.assertTrue(s.time_synced)
        s.run()

    def test_clock_sync_reports_error_but_continues(self) -> None:
        self.board.throw_rtc = True
        # with self.assertRaises(Exception):
        s = SensorBox(self.board, self.screen, self.config)
        self.assertIn("SYNC", s.board.printed_messages_for_testing)

    def test_sensor_config_reports_error_but_continues(self) -> None:
        self.board.throw_http = True
        s = SensorBox(self.board, self.screen, self.config)
        self.assertIn("sensor config", s.board.printed_messages_for_testing)

    def test_wifi_disconnected_reports_error_but_continues(self) -> None:
        self.board.wifi_connect = False
        s = SensorBox(self.board, self.screen, self.config)
        self.assertIn("CHECK", s.screen.displayed_messages_for_testing)
        s.run()
        self.assertIn("DISCONNECTED", s.screen.displayed_messages_for_testing)

    def test_normal_run(self) -> None:
        s = SensorBox(self.board, self.screen, self.config)
        s.run()

    def test_tries_to_run_without_wifi(self) -> None:
        self.board.wifi_connect = False
        s = SensorBox(self.board, self.screen, self.config)
        s.run()

    def test_tries_to_run_with_sensor_read_failure(self) -> None:
        self.board.ds18x20_read_failure = True
        s = SensorBox(self.board, self.screen, self.config)
        s.run()

    def test_dev_mode_works(self) -> None:
        dev_mode_board = BoardMock(watchdog_enabled=False)
        s = SensorBox(dev_mode_board, self.screen, self.config)
        with self.assertRaises(RuntimeError):
            s.run()  # dev mode leaves system hanging, which in testing throws an exception

    def test_phase_network_gets_setup(self) -> None:
        s = SensorBox(self.board, self.screen, self.config)
        s.time_synced = False
        s.retrieved_sensor_info = False
        s.phase_network()
        s.time_synced = True
        s.retrieved_sensor_info = True

    def test_phase_push_handles_conditions(self) -> None:
        s = SensorBox(self.board, self.screen, self.config)
        s.time_synced = False
        previous_push_time_stamp = s.last_push_stamp
        s.phase_push(True)  # should leave early without changing anything or throwing any errors
        self.assertEqual(previous_push_time_stamp, s.last_push_stamp)
        self.assertFalse(s.last_push_had_errors)
        s.time_synced = True
        s.last_push_ms = int(time()) * 1000
        s.phase_push(False)  # not the first time, and not enough time passed, so it shouldn't have pushed yet
        self.assertEqual(previous_push_time_stamp, s.last_push_stamp)
        self.assertFalse(s.last_push_had_errors)
        # in an http throw, there should be errors
        s.board.throw_http = True  # type: ignore[attr-defined]
        s.phase_push(True)  # call with a first time true so it definitely tries to push
        self.assertTrue(s.last_push_had_errors)

    def test_various_display_conditions(self) -> None:
        temp_pairs = {
            -30.0: "-22",
            -20.1: "-4",
            -14: "6",
            -3: "26",
            40: "104",
        }
        for c, f in temp_pairs.items():
            board = BoardMock(fixed_temperature_c=c)
            s = SensorBox(board, self.screen, self.config)
            s.run()
            self.assertIn(f, s.screen.displayed_messages_for_testing)

    def test_trying_to_connect_to_wifi(self) -> None:
        board = BoardMock(override_wifi_ssids=["Dummy", "WiFiNetworkOne"])
        s = SensorBox(board, self.screen, self.config)
        s.try_to_connect_to_wifi()
        self.assertTrue(s.board.isconnected())

    def test_trying_to_connect_to_wifi_2(self) -> None:
        board = BoardMock(wifi_connect=False)
        s = SensorBox(board, self.screen, self.config)
        s.try_to_connect_to_wifi()
        self.assertFalse(s.board.isconnected())

    def test_updating_sensors(self) -> None:
        board_no_sensors = BoardMock(empty_ds18x20_roms=True)
        s = SensorBox(board_no_sensors, self.screen, self.config)
        self.assertFalse(s.sensors)  # empty
        s.update_temperatures()  # should just return fine
        board_failed_conversion = BoardMock(convert_temp_failure=True)
        s = SensorBox(board_failed_conversion, self.screen, self.config)
        with self.assertRaises(Exception):
            s.update_temperatures()  # the update_temperatures function should throw

    def test_update_display_issues(self) -> None:
        s = SensorBox(self.board, self.screen, self.config)
        s.run()
        s.last_temp_stamp = ()
        s.update_display()
        self.assertIn("NEVER", s.screen.displayed_messages_for_testing)
        s.last_push_had_errors = True
        s.update_display()
        self.assertIn("Had Errors", s.screen.displayed_messages_for_testing)

    def test_try_syncing_time_fails_on_ntp(self) -> None:
        board = BoardMock(bad_ntp_timestamp=True)
        s = SensorBox(board, self.screen, self.config)
        s.try_to_sync_time()
        self.assertFalse(s.time_synced)

    def test_sensor_details_bad_get(self) -> None:
        board = BoardMock(bad_http_get_status=True)
        s = SensorBox(board, self.screen, self.config)
        s.retrieved_sensor_info = False
        s.try_to_get_sensor_details()
        self.assertFalse(s.retrieved_sensor_info)

    def test_sensor_details_missing_label(self) -> None:
        board = BoardMock(label_missing_from_rom_hex_map=True)
        s = SensorBox(board, self.screen, self.config)
        self.assertFalse(s.retrieved_sensor_info)

    def test_sensor_details_missing_in_sensors(self) -> None:
        board = BoardMock(watchdog_enabled=True, label_missing_from_sensors=True)
        s = SensorBox(board, self.screen, self.config)
        self.assertFalse(s.retrieved_sensor_info)

    def test_put_to_github_handling(self) -> None:
        board = BoardMock(watchdog_enabled=True, bad_http_put_status=True)
        s = SensorBox(board, self.screen, self.config)
        s.push_to_github()
        self.assertIn("PUT Error", s.board.printed_messages_for_testing)

    # TODO: Think about turning these unit tests into operational issues:
    # def test_wifi_is_down(self):
