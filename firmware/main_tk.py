from firmware.config_local_server import ConfigLocalServer
from firmware.sensing import SensorBox
from firmware.screen_tk import ScreenTk
from firmware.board_tk import BoardTk


def main() -> int:
    screen = ScreenTk()
    config = ConfigLocalServer(valid_config=True)
    board = BoardTk(watchdog_enabled=True)
    r = SensorBox(board, screen, config)
    r.run()
    return 0


if __name__ == "__main__":
    main()
