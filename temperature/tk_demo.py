from sensing import OperatingMode, SensorBox


def main():
    r = SensorBox(OperatingMode.MockWindow)
    r.run()


if __name__ == "__main__":
    main()
