# Temperature Sensors

[![Build and deploy GitHub Pages](https://github.com/okielife/TempSensors/actions/workflows/pages.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/pages.yml)
[![Check All Temperatures](https://github.com/okielife/TempSensors/actions/workflows/check_all_temps.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/check_all_temps.yml)
[![Clean Old Results](https://github.com/okielife/TempSensors/actions/workflows/clean_old_results.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/clean_old_results.yml)
[![Scheduled Sensor Responsiveness Check](https://github.com/okielife/TempSensors/actions/workflows/check_sensor_responsiveness.yml/badge.svg)](https://github.com/okielife/TempSensors/actions/workflows/check_sensor_responsiveness.yml)

My goal with this repo is to provide everything needed for someone to construct and stand up one of the temperature sensor boxes.  
This includes the box design, hardware specs, and code.  
I will try my best to move in major version chunks together, so that if I make a design change, it is directly reflected in the code, hardware, design, etc., all at once.  
Then someone can download a single release and get everything.

This repo stores all firmware and site build rules in the main branch.
The dashboard is a jekyll project stored in the dashboard folder that renders temperature sensor data.
The sensor data is actually stored in the gh-pages branch, but checked out into sensor_data when rendering or running scripts.
The repo also contains scripts/ to clean old results and run tests on the results.

The dashboard is available here: https://okielife.github.io/TempSensors

To adjust the configuration, edit the file here: https://github.com/okielife/TempSensors/edit/main/dashboard/_data/config.json

# Repo Structure

firmware/
etc.

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