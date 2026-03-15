# this file will scan the _posts folder and append a representative "average" temperature value for each sensor to
# the dashboard/_data/history.json file

from datetime import datetime, timezone
from json import dumps, loads
from pathlib import Path
from sys import argv

data_root = Path(argv[1])  # pass path to the sensor_data/data folder in a standalone clone

# read the current config and history from the dashboard folder in the main branch
this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
config_file = repo_root / 'dashboard' / '_data' / 'config.json'
config = loads(config_file.read_text())
history_file = repo_root / 'dashboard' / '_data' / 'history.json'
current_history = loads(history_file.read_text())

# loop over every post, appending temperatures to create large lists
all_posts = data_root.glob('**/*.html')
all_posts_list = list(all_posts)
current_temperature_history = dict()
for post in all_posts_list:
    sensor_id = None
    temperature = None
    contents = post.read_text()
    for line in contents.split('\n'):
        if 'sensor_id' in line:
            sensor_id = line.split(':')[1].strip()
        elif 'temperature' in line:
            temperature = float(line.split(':')[1].strip())
    if sensor_id is None or temperature is None:
        print(f"Bad sensor data in file {post}; sensor_id = {sensor_id} temperature = {temperature}")
        continue
    if sensor_id not in current_temperature_history:
        current_temperature_history[sensor_id] = []
    current_temperature_history[sensor_id].append(temperature)

# calculate average values for each sensor over the known reporting period
average_values = {}
for sensor_id, temperature_list in current_temperature_history.items():
    sensor_label = config['rom_hex_to_cable_number'][sensor_id]
    sensor_nice_name = config['sensors'][sensor_label]['nice_name']
    sorted_temps = sorted(temperature_list)
    if len(sorted_temps) > 10:
        sorted_temps = sorted_temps[4:-4]  # get rid of any random outliers
    average_temp = sum(sorted_temps) / len(sorted_temps)  # it _will_ have at least one based on logic above
    average_values[sensor_nice_name] = average_temp

# grab a nice timestamp to represent the current reading
current_utc_datetime = datetime.now(timezone.utc)
utc_string = current_utc_datetime.strftime('%Y-%m-%d')

# save the new history to file
current_history[utc_string] = average_values
with open(history_file, 'w') as outfile:
    outfile.write(dumps(current_history, indent=2))
print(f"dashboard/_data/history.json updated, next `git add -A`, `git commit -m MSG` and `git push origin main")
