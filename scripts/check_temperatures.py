# this file will scan the _posts folder and look for the most recent N results for each sensor folder
# it will compare the temperatures to the max temps and fail if any of them are out of range

from datetime import datetime, timedelta
from json import loads
from pathlib import Path
from subprocess import check_output, CalledProcessError
from sys import argv, exit

from pytz import timezone, utc


if len(argv) < 2:
    print("Must pass in the latest SHA for this file to find the last update")
    exit(2)

this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
posts_dir = repo_root / '_posts'
config_file = repo_root / '_data' / 'config.json'
config = loads(config_file.read_text())

if argv[1] == 'all':
    sensor_ids_to_check = set([x['id'] for x in config['sensors']])
else:  # get it from the files changed in this git commit SHA
    try:
        # initial_git_commit = check_output(
        #     ['git', 'diff-tree', argv[1], '-r'], cwd=str(repo_root)
        # )
        # print(initial_git_commit)
        git_response = check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', argv[1], '-r'], cwd=str(repo_root)
        )
        print(git_response)
    except CalledProcessError as cpe:
        print("Could not run Git command to mine out files, aborting")
        exit(2)
    git_response_string = git_response.decode('utf-8')
    files_changed = git_response_string.split('\n')
    interesting_files = [repo_root / f for f in files_changed if f.startswith('_posts/') and f.endswith('.html')]
    sensor_ids_to_check = set()
    for i in interesting_files:
        sensor_name = i.parts[-2]
        sensor_ids_to_check.add(sensor_name)

active_sensors = config['sensors']
active_sensor_ids = [s['id'] for s in active_sensors]

time_zone_cst = timezone('America/Chicago')
utc_time_now = datetime.now(utc)
central_standard_time_now = utc_time_now.astimezone(time_zone_cst)
two_hours_ago_in_cst = central_standard_time_now - timedelta(hours=2)

print(f"Going to check any temperature sensor values from after this time stamp: {two_hours_ago_in_cst}")

failed = []
passed = []
ignored = []

for sensor in sensor_ids_to_check:
    print(f"Processing sensor with ID: {sensor}")
    # skip if this sensor is not part of the active list
    if sensor not in active_sensor_ids:
        ignored.append(sensor)
        continue

    # get our main settings for this sensor from config.json
    this_sensor = [s for s in active_sensors if s['id'] == sensor][0]  # must be there
    location = this_sensor['sensor_location']
    max_temp = this_sensor.get('maximum_temp', '3')
    max_temp = float(max_temp)

    # check the recent several for out of range, only fail if they all fail
    this_sensor_post_dir = posts_dir / sensor
    # get a list of the posts for this sensor, sorted and in reverse time (most recent first)
    # that way we can iterate over them and once we reach an hour
    all_posts_this_sensor = this_sensor_post_dir.glob('*.html')
    sorted_posts = sorted(all_posts_this_sensor)
    ordered_posts = sorted_posts[::-1]
    temp_history = []
    # figure out how long ago 2 hours was, if there are any valid temps in the last 2 hours, lets say it's fine
    for p in ordered_posts:
        file_name = p.name
        time_stamp = file_name.split('_')[0]
        time_zone_naive_post_time = datetime.strptime(time_stamp, '%Y-%m-%d-%H-%M-%S')
        cst_aware_post_time = time_zone_cst.localize(time_zone_naive_post_time)
        if cst_aware_post_time >= two_hours_ago_in_cst:
            yaml_lines = yaml_content = p.read_text().split('\n')
            temp = '*unknown_temperature*'
            for line in yaml_lines:
                tokens = line.strip().split(':')
                if tokens[0].strip() == 'temperature':
                    temp = tokens[1].strip()
                    float_temp = float(temp)
                    temp_history.append(float_temp)
                    break
            print(f" Found a recent sensor value to test with timestamp: {time_zone_naive_post_time} and value {temp}")
        else:
            print(" Reached time stamp older than 2 hours ago, stopping scanning this sensor")
            break
    if not temp_history:
        failed.append(
            f"EMPTY TEMP HISTORY - weird; ID: {sensor}; Location: {location}; MaxTemp: {max_temp}"
        )
    elif all([x > max_temp for x in temp_history]):
        failed.append(
            f"Temp HIGH; ID: {sensor}; Location: {location}; MaxTemp: {max_temp}; Temp History: {temp_history}"
        )
    else:
        passed.append(
            f"Temp GOOD! ID: {sensor}; Location: {location}; MaxTemp: {max_temp}; Temp History: {temp_history}"
        )

if failed:
    failure_string = ''.join(['\n - ' + f for f in failed])
else:
    failure_string = '*NONE FAILING*'
checked_string = ''.join(['\n - ' + s for s in passed])
ignored_string = ''.join(['\n - ' + s for s in ignored])
print("\n ******** SUMMARY RESULTS ********")
print(f"Sensors Passing:{checked_string}\nSensors Ignored:{ignored_string}\nSensors Failing:{failure_string}")

if failed:
    print("\n **** At least one sensor failed, exiting with code 1")
    exit(1)
else:
    exit(0)
