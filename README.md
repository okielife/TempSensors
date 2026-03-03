# Temperature Sensors

This repository (hopefully) contains everything needed to create and manage our temperature sensor system.
We primarily use these temperature sensors to monitor temperatures of fridges and freezers at a local food pantry.
The sensors are built from Raspberry Picos running MicroPython with DS18x20 one-wire sensors and TFT displays inside 3D printed cases.
My intention is to make this as open source as possible, where the only "secret" is the GitHub token used to write the sensor results up to the dashboard repo. 
This repo contains design information, 3D print models, assembly instructions, documentation, firmware code, CI automated testing, and the Jekyll dashboard build.

## Badges that should always be green

[![Dashboard Deployment](https://github.com/okielife/TempSensors/actions/workflows/pages.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/pages.yml)
[![Firmware Code Tests](https://github.com/okielife/TempSensors/actions/workflows/firmware_tests.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/firmware_tests.yml)
[![Stale Sensor Data Cleanup](https://github.com/okielife/TempSensors/actions/workflows/clean_old_results.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/clean_old_results.yml)
[![Static Code Analysis](https://github.com/okielife/TempSensors/actions/workflows/mypy.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/mypy.yml)

## Badges that might not be green

[![Temperature(s) out of Range](https://github.com/okielife/TempSensors/actions/workflows/check_all_temps.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/check_all_temps.yml)
[![Unresponsive sensor(s)](https://github.com/okielife/TempSensors/actions/workflows/check_sensor_responsiveness.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/check_sensor_responsiveness.yml)

## Convenient Links

- [Live dashboard](https://okielife.github.io/TempSensors) (updated every 30 minutes or so) 
- [Sensor configuration](https://github.com/okielife/TempSensors/edit/main/dashboard/_data/config.json) (for easy adjustment as sensors are changed/added) 
- [Latest Documentation]([ReadTheDocs](https://tempsensors.readthedocs.io/en/latest/)) on ReadTheDocs

## Documentation

[![Latest Docs](https://app.readthedocs.org/projects/tempsensors/badge/?version=latest&style=flat)](https://tempsensors.readthedocs.io/en/latest/)

The repository is documented on [ReadTheDocs](https://tempsensors.readthedocs.io/en/latest/) from the source in the repo [docs/](https://github.com/okielife/TempSensors/tree/main/docs) folder.
The documentation covers details about the project, parts lists, assembly instructions, wiring diagrams, and more.
The documentation will soon also include module documentation for everything in the [firmware](https://github.com/okielife/TempSensors/tree/main/firmware) directory.

## Repository Structure and More

The repository is structured with two "permanent" branches:
 - The `main` branch contains all the firmware code, design files, tests, scripts, models, docs, and the build rules and assets for the dashboard.
 - The `sensor_data` branch contains purely the posted results from the sensors, so that these never get in the way of development branches. 

The code in the repository consists of:
 - `.github/workflows`: The yaml workflows that are run either on each commit, pull request, or on a schedule
 - `dashboard`: The Jekyll based dashboard site, including html templates and snippets, Jekyll configuration, and static data and assets
 - `docs`: The Sphinx-based RestructuredText documentation that is posted to ReadTheDocs, consisting of hand-written design discussion, assembly instructions, parts list, and soon firmware module documentation
 - `firmware`: The Python-based firmware, with MicroPython-based code to actually be executed on the Pico, but with supporting Python code to mock behavior for unit testing and even a Tk-based class to mimic the display in a Tk window
 - `model`: This folder currently just contains a couple 3D model files, but eventually will hold lots of supporting information, maybe design discussion, and more.
 - `scripts`: Both Python and Bash scripts that are used to support development, both locally and inside GitHub Action instances

The versioning of this project is going to mimic semantic versioning.
I anticipate a major release of v4.0 soon, after which any small tweaks worth a release will be 4.1, etc.
More substantial changes for future cases and hardware will trigger a major version bump to 5.0.
I plan to package up all assets necessary for a build into a single downloadable package when I tag a new release version.
The roadmap for all these ideas will be tracked on the [milestones](https://github.com/okielife/TempSensors/milestones) page.

# Development

One time, do this: 

```
clone
git worktree add sensor_data gh-pages
pip install -r requirements
```

For firmware development, you can run tests like this:

```
coverage run -m unittest discover -s firmware/tests
```

To run scripts on the sensor data or reproduce the dashboard locally, make sure your sensor data is up to date:

```
python3 scripts/refresh_sensor_data.sh
```

Then run any script:

```
python3 scripts/whatever
```

or build the dashboard

```angular2html
cd dashboard
bundle exec jekyll serve
```
