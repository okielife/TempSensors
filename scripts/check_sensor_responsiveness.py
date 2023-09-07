# this file will check to see how long it has been since each sensor responded
# if it is too long, then the workflow will fail

from datetime import datetime, timedelta
from json import loads
from pathlib import Path
from sys import exit

max_allowed_delay_days = 1
current_time = datetime.utcnow()
cutoff_date = current_time - timedelta(days=max_allowed_delay_days)
print(f"Checking responsiveness\n - Current time: {current_time}\n - Cutoff time: {cutoff_date}")
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

    time_string = "{invalid_time_string}"
    measurement_time = datetime.now() - timedelta(days=999)
    try:
        file_name = post.name
        time_string = file_name.split('_')[0]
        measurement_time = datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S')
    except Exception as e:
        print(f"Could not create timestamp for file: \"{post}\"; Reason: {e}")

    # if we've made it this far, mark down that we checked this one
    sensors_checked.add(f"ID: {sensor_id_from_post_file}; Most Recent Update {time_string} UTC")
    sensors_handled_already.add(sensor_id_from_post_file)

    if measurement_time < cutoff_date:
        failures.append(
            f"Sensor Unresponsive; ID: {sensor_id_from_post_file}; Most Recent Update {time_string} UTC"
        )
if failures:
    failure_string = ''.join(['\n - ' + f for f in failures])
    print(f"At least one active sensor it not responding!\nFailures listed here:{failure_string}")
    exit(1)
else:
    checked_string = ''.join(['\n - ' + s for s in sensors_checked])
    ignored_string = ''.join(['\n - ' + s for s in sensors_ignored])
    print(f"Sensors Responding Nicely!\nSensors Checked:{checked_string}\nSensors Ignored:{ignored_string}")
    exit(0)
