# this file will scan the _posts folder and look for the most recent N results for each sensor folder
# it will compare the temperatures to the max temps and fail if any of them are out of range

from json import loads
from pathlib import Path
from sys import exit


this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent

config_file = repo_root / '_data' / 'config.json'
config = loads(config_file.read_text())
active_sensors = config['sensors']
active_sensor_ids = [s['id'] for s in active_sensors]

posts_folder = repo_root / '_posts'
all_posts = posts_folder.glob('**/*.html')
all_posts_list = reversed(sorted(all_posts))  # should put the most recent first
sensors_handled_already = set()
failures = []
sensors_checked = set()
sensors_ignored = set()
for post in all_posts_list:
    sensor_id_from_post_file = post.parts[-2]  # should be the sensor ID subdirectory
    # skip if this sensor is not part of the active list
    if sensor_id_from_post_file not in active_sensor_ids:
        sensors_ignored.add(sensor_id_from_post_file)
        continue
    # skip if we've already checked this sensor ID
    if sensor_id_from_post_file in sensors_handled_already:
        continue

    # if we've made it this far, mark down that we checked this one
    sensors_checked.add(sensor_id_from_post_file)
    sensors_handled_already.add(sensor_id_from_post_file)

    # get our main settings for this sensor from config.json
    this_sensor = [s for s in active_sensors if s['id'] == sensor_id_from_post_file][0]  # must be there
    location = this_sensor['sensor_location']
    max_fridge_temp = this_sensor.get('maximum_fridge_temp', '3')
    max_fridge_temp = float(max_fridge_temp)
    max_freezer_temp = this_sensor.get('maximum_freezer_temp', '-10')
    max_freezer_temp = float(max_freezer_temp)

    # then get the measurements from the post file itself
    yaml_content = post.read_text().split('---')[1].strip()
    yaml_lines = yaml_content.split('\n')
    yaml_dict = dict()
    for line in yaml_lines:
        tokens = line.strip().split(':')
        yaml_dict[tokens[0].strip()] = tokens[1].strip()
    sensor_id = yaml_dict.get('sensor_id', '-InvalidOrMissingSensorID')
    fridge_temp = yaml_dict.get('fridge_temp', None)
    freezer_temp = yaml_dict.get('freezer_temp', None)
    if fridge_temp:
        float_fridge_temp = float(fridge_temp)
        if float_fridge_temp > max_fridge_temp:
            failures.append(
                f"Fridge HIGH; ID: {sensor_id}; Location: {location}; MaxTemp: {max_fridge_temp}; Temp: {fridge_temp}"
            )
    if freezer_temp:
        float_freezer_temp = float(freezer_temp)
        if float_freezer_temp > max_freezer_temp:
            failures.append(
                f"Freeze HIGH; ID: {sensor_id}; Location: {location}; MaxTemp: {max_freezer_temp}; Temp: {freezer_temp}"
            )
if failures:
    failure_string = ''.join(['\n - ' + f for f in failures])
    print(f"At least one measurement failed!\nFailures listed here:{failure_string}")
    exit(1)
else:
    checked_string = ''.join(['\n - ' + s for s in sensors_checked])
    ignored_string = ''.join(['\n - ' + s for s in sensors_ignored])
    print(f"Temperature Measurements Passing!\nSensors Checked:{checked_string}\nSensors Ignored:{ignored_string}")
    exit(0)
