# this file will check to see how long it has been since each sensor responded
# if it is too long, then the workflow will fail

from datetime import datetime, timedelta, UTC
from json import loads
from pathlib import Path
from sys import exit


RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

# we are now reporting temperature measurement time in UTC
# use 18 hours as a reasonable amount of hours to report an unresponsive sensor
max_allowed_delay_hours = 18
current_time = datetime.now(UTC)
cutoff_date = current_time - timedelta(hours=max_allowed_delay_hours)
print(f"Checking responsiveness\n - Current time: {current_time} UTC\n - Cutoff time: {cutoff_date} UTC")
this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent

# grab some data from the config file, ignoring any readme*s
config_file = repo_root / '_data' / 'config.json'
config = loads(config_file.read_text())
active_sensors = config['sensors']
active_sensor_roms = []
for k in active_sensors:
    if not k.startswith('readme'):
        active_sensor_roms.append(active_sensors[k]["hex"])
active_sensors_checked = {x: False for x in active_sensor_roms}
hex_map = config['rom_hex_to_cable_number']

# loop over all the latest posts, just operating on the most recent from each
posts_folder = repo_root / '_posts'
all_posts = posts_folder.glob('**/*.html')
all_posts_list = reversed(sorted(all_posts))  # should put the most recent first
sensors_handled_already = set()
failures = []
sensors_checked = set()
sensors_ignored = set()
for post in all_posts_list:
    sensor_rom = post.parts[-2]  # should be the sensor ID subdirectory
    # skip if this sensor is not part of the active list
    if sensor_rom not in active_sensor_roms:
        sensors_ignored.add(sensor_rom)
        continue

    # skip if we've already checked this sensor ID
    if sensor_rom in sensors_handled_already:
        continue

    cable_num = hex_map[sensor_rom]
    nice_name = active_sensors[cable_num]["nice_name"]
    time_string = post.name.split('_')[0]  # files expected to be named _posts/YYYY-MM-DD-HH-MM-SS_something.html
    time = datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S').replace(tzinfo=UTC)

    # if we've made it this far, mark down that we checked this one
    sensors_checked.add(f"{nice_name} ({cable_num}: {sensor_rom}): Latest Update {time} UTC")
    sensors_handled_already.add(sensor_rom)
    active_sensors_checked[sensor_rom] = True

    # and if this most recent post was too old, mark it as a failure
    if time < cutoff_date:
        failures.append(
            f"Sensor Unresponsive; {nice_name} ({cable_num}: {sensor_rom}); Latest Update {time} UTC"
        )

for sensor_id in active_sensors_checked:
    if not active_sensors_checked[sensor_id]:
        failures.append(f"{sensor_id} data missing - typo?")

failure_string = ''.join([f"\n{RED} - {f}{ENDC}" for f in failures])
checked_string = ''.join([f"\n - {s}" for s in sensors_checked])
ignored_string = ''.join([f"{YELLOW}\n - {s}{ENDC}" for s in sensors_ignored])

if failures:
    failure_string = ''.join([f"\n{RED} - {f}{ENDC}" for f in failures])
    print(f"At least one active sensor it not responding!\nFailures listed here:{failure_string}\nSensors Checked:{checked_string}\nSensors Ignored:{ignored_string}\nSensors Ignored:{sensors_ignored}")
    exit(1)
else:
    print(f"{GREEN}Sensors Responding!{ENDC}\nSensors Checked:{checked_string}\nSensors Ignored:{ignored_string}")
