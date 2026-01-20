# this file will scan the _posts folder and look for the most recent N results for each sensor folder
# it will compare the temperatures to the max temps and fail if any of them are out of range

from json import loads
from pathlib import Path
from sys import exit


RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
posts_folder = repo_root / '_posts'

failures = []
sensors_passing = set()
sensors_ignored = set()

config_file = repo_root / '_data' / 'config.json'
config = loads(config_file.read_text())
active_sensors = config['sensors']
for cable_num, active_sensor in active_sensors.items():
    if cable_num.startswith('readme'):
        continue
    sensor_rom = active_sensor['hex']
    max_temp = float(active_sensor['maximum_temp'])
    nice_name = active_sensor['nice_name']
    sensor_posts_folder = posts_folder / sensor_rom
    all_posts_this_sensor = sorted(sensor_posts_folder.glob('*.html'))
    up_to_last_three = all_posts_this_sensor[-3:][::-1]
    measured_temps = []
    for post in up_to_last_three:
        # then get the measurements from the post file itself
        yaml_content = post.read_text().split('---')[1].strip()
        yaml_lines = yaml_content.split('\n')
        for yaml_line in yaml_lines:
            if 'temperature' in yaml_line:
                measured_temps.append(float(yaml_line.split(':')[1].strip()))
                break
    if len(measured_temps) == 0:
        sensors_ignored.add(f"No data for sensor: {nice_name}({cable_num}: {sensor_rom})")
    else:
        if any([f < max_temp for f in measured_temps]):
            sensors_passing.add(
                f"Temperature GOOD! {nice_name} ({cable_num}: {sensor_rom}; Max Temp: {max_temp}; Temp History: {measured_temps}"
            )
        else:
            failures.append(
                f"Temperature HIGH; {nice_name} ({cable_num}: {sensor_rom}; Max Temp: {max_temp}; Temp History: {measured_temps}"
            )

checked_string = ''.join([f"\n{GREEN} - {s}{ENDC}" for s in sensors_passing])
ignored_string = ''.join([f"\n{YELLOW} - {s}{ENDC}" for s in sensors_ignored])
failure_string = ''.join([f"\n{RED} - {f}{ENDC}" for f in failures])
if failures:
    print(f"At least one measurement failed!\nFailures listed here:{failure_string}\nSensors Passing:{checked_string}\nSensors Ignored:{ignored_string}")
    exit(1)
else:
    print(f"{GREEN}Sensors Passing!{ENDC}\n{checked_string}\nSensors Ignored:{ignored_string}")
