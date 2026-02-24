from temperature.sensing import SensorBox
from temperature.screen_tk import ScreenTk
from temperature.board_tk import BoardTk


def main():
    t = ScreenTk()
    n = BoardTk(continue_running_after_first_iteration=True)
    r = SensorBox(t, n)
    r.run()


if __name__ == "__main__":
    main()
