from temperature.sensing import SensorBox
from temperature.screen_tk import ScreenTk
from temperature.board_tk import BoardTk
from temperature.config_template import WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN


def main():
    screen = ScreenTk()
    board = BoardTk(watchdog_enabled=False, continue_running_after_first_iteration=True)
    r = SensorBox(board, screen, WIFI_NETWORKS, CONNECTED_SENSORS, GITHUB_TOKEN)
    r.run()


if __name__ == "__main__":
    main()
