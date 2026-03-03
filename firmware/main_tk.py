from firmware.config_local_server import ConfigLocalServer
from firmware.sensing import SensorBox
from firmware.screen_tk import ScreenTk
from firmware.board_tk import BoardTk


def main():
    screen = ScreenTk()
    config = ConfigLocalServer()
    board = BoardTk()
    r = SensorBox(board, screen, config)
    r.run()


if __name__ == "__main__":
    main()
