try:
    from sensor_config import github_token, sensor_id, sensor_location
except ImportError:
    from os import environ
    github_token = environ['SENSOR_TOKEN']
    sensor_id = 'ABC'
    sensor_location = 'Place'
from base64 import b64encode
from datetime import datetime
from json import dumps
from random import randint
from requests import put
from time import sleep

sensing_interval = 10 * 60  # 10 minutes, in seconds
commit_interval = 60 * 60  # 1 hour, in seconds


while True:
    # check for wifi, connect if needed

    # check temperature(s)
    fridge_temp = randint(0, 10)
    freezer_temp = randint(-15, 0)

    # update screen (if applicable)

    # if commit interval is passed:
    #  create new html content file
    #  update using github api
    file_content = f"""
---
sensor_id: {sensor_id}
location: {sensor_location}
fridge_temperature: {fridge_temp}
freezer_temperature: {freezer_temp}
---
{{}}
    """
    current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_name = f"{current}_{sensor_location}_{sensor_id}.html"
    file_path = f"_posts/{sensor_id}/{file_name}"
    url = f"https://api.github.com/repos/okielife/TempSensors/contents/{file_path}"
    headers = {
        'Accept': 'application/vnd.github + json',
        'Authorization': f'Token {github_token}'
        # 'Authorization': f'Bearer {github_token}'
    }
    encoded_content = b64encode(file_content.encode()).decode()
    data = {
        'message': f"Updating {file_path}",
        'content': encoded_content
    }
    response = put(url, headers=headers, data=dumps(data))
    if response.status_code == 201:
        print("File created successfully.")
    elif response.status_code == 200:
        print("File updated successfully.")
    else:
        print("Error:", response.text)

    # sleep until next sensing time
    sleep(sensing_interval)
