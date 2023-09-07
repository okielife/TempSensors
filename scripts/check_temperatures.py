# this file will scan the _posts folder and look for the most recent N results for each sensor folder
# it will compare the temperatures to the max temps and fail if any of them are out of range

from pathlib import Path
from sys import exit

sensor_ids_to_ignore = [
    'some_old_sensor_id'
]

this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
posts_folder = repo_root / '_posts'
all_posts = posts_folder.glob('**/*.html')
all_posts_list = reversed(sorted(all_posts))  # should put the most recent first
sensors_handled_already = set()
failures = []
sensors_checked = []
sensors_ignored = []
for post in all_posts_list:
    sensor_id = post.parts[-2]  # should be the sensor ID subdirectory
    if sensor_id in sensor_ids_to_ignore:
        sensors_ignored.append(sensor_id)
        continue
    if sensor_id in sensors_handled_already:
        continue
    sensors_checked.append(sensor_id)
    sensors_handled_already.add(sensor_id)
    yaml_content = post.read_text().split('---')[1].strip()
    yaml_lines = yaml_content.split('\n')
    yaml_dict = dict()
    for line in yaml_lines:
        tokens = line.strip().split(':')
        yaml_dict[tokens[0].strip()] = tokens[1].strip()
    sensor_id = yaml_dict.get('sensor_id', '-InvalidOrMissingSensorID')
    location = yaml_dict.get('location', 'InvalidOrMissingSensorLocation')
    fridge_temp = yaml_dict.get('fridge_temp', None)
    max_fridge_temp = yaml_dict.get('maximum_fridge_temp', '3')
    max_fridge_temp = float(max_fridge_temp)
    freezer_temp = yaml_dict.get('freezer_temp', None)
    max_freezer_temp = yaml_dict.get('maximum_freezer_temp', '-10')
    max_freezer_temp = float(max_freezer_temp)
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
