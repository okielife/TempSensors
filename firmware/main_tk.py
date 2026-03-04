from firmware.config_local_server import ConfigLocalServer
from firmware.sensing import SensorBox
from firmware.screen_tk import ScreenTk
from firmware.board_tk import BoardTk


def main() -> int:
    """
    This is the entry point for developer mode using a Tk Window as the display. This class otherwise behaves
    similar to the hardware main entry point, in that it creates a screen, config, and board before passing them
    to the actual sensor class to run.

    Note that this Tk window is not updated on a Tk main loop like a typical application.  It is updated exactly like
    the hardware, so you cannot easily kill the Window by clicking the X close button, you need to shut down the
    underlying main process or kill the debugger.

    :return: Nothing
    """
    screen = ScreenTk()
    config = ConfigLocalServer(valid_config=True)
    board = BoardTk(watchdog_enabled=True)
    r = SensorBox(board, screen, config)
    r.run()
    return 0


if __name__ == "__main__":
    main()
