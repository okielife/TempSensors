# this file will scan the _posts folder and look for the most recent N results for each sensor folder
# it will compare the temperatures to the max temps and fail if any of them are out of range

from json import loads
from pathlib import Path
from subprocess import check_output, CalledProcessError
from sys import argv, exit


if len(argv) != 2:
    print("Must pass in the latest SHA for this file to find the last update")
    exit(2)

this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
posts_dir = repo_root / '_posts'

config_file = repo_root / '_data' / 'config.json'
config = loads(config_file.read_text())

try:
    initial_git_commit = check_output(
        ['git', 'diff-tree', argv[1], '-r'], cwd=str(repo_root)
    )
    print(initial_git_commit)
    git_response = check_output(
        ['git', 'diff-tree', '--no-commit-id', '--name-only', argv[1], '-r'], cwd=str(repo_root)
    )
except CalledProcessError as cpe:
    print("Could not run Git command to mine out files, aborting")
    exit(2)

git_response_string = git_response.decode('utf-8')
files_changed = git_response_string.split('\n')
interesting_files = [repo_root / f for f in files_changed if f.startswith('_posts/') and f.endswith('.html')]

updated_sensors = set()
for i in interesting_files:
    sensor_name = i.parts[-2]
    updated_sensors.add(sensor_name)

active_sensors = config['sensors']
active_sensor_ids = [s['id'] for s in active_sensors]

failures = []
sensors_passing = set()
sensors_ignored = set()
for sensor in updated_sensors:
    # skip if this sensor is not part of the active list
    if sensor not in active_sensor_ids:
        sensors_ignored.add(sensor)
        continue

    # get our main settings for this sensor from config.json
    this_sensor = [s for s in active_sensors if s['id'] == sensor][0]  # must be there
    location = this_sensor['sensor_location']
    max_temp = this_sensor.get('maximum_temp', '3')
    max_temp = float(max_temp)

    # check the recent several for out of range, only fail if they all fail
    # TODO: Change this to check the entire last ... hour ... or so, not a fixed number of them
    #       That way if sample intervals vary, this will still handle the right amount of time
    this_sensor_post_dir = posts_dir / sensor
    sorted_posts = sorted(this_sensor_post_dir.glob('*.html'))
    temperature_history = []
    max_num_to_check = 12
    for p in sorted_posts[-max_num_to_check:]:  # take up to the last 3
        yaml_content = p.read_text().split('---')[1].strip()
        yaml_lines = yaml_content.split('\n')
        for line in yaml_lines:
            tokens = line.strip().split(':')
            if tokens[0].strip() == 'temperature':
                temp = tokens[1].strip()
                float_temp = float(temp)
                temperature_history.append(float_temp)
    hist = temperature_history
    if all([x > max_temp for x in temperature_history]):
        failures.append(f"Temp HIGH; ID: {sensor}; Location: {location}; MaxTemp: {max_temp}; Temp History: {hist}")
    else:
        sensors_passing.add(f"Temp GOOD! ID: {sensor}; MaxTemp: {max_temp}; Temp History: {hist}")

if failures:
    failure_string = ''.join(['\n - ' + f for f in failures])
    print(f"At least one measurement failed!\nSensors Failing:{failure_string}")
checked_string = ''.join(['\n - ' + s for s in sensors_passing])
ignored_string = ''.join(['\n - ' + s for s in sensors_ignored])
print(f"Sensors Passing:{checked_string}\nSensors Ignored:{ignored_string}")

if failures:
    exit(1)
else:
    exit(0)
