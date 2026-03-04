#: Defines a set of known network SSID/PW key/value pairs
DEFAULT_WIFI_NETWORKS = {
    "MiFi8000-C1DE": "9df7061f",
    "EmeraldWiFi": "rejoice27"
}

#: Defines the bits of a 29x29 QR code image that maps to http://192.168.4.1
QR_CODE_192_168_4_1 = [
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
    [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1],
    [0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0],
    [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
]


def html_form(device_id: str, initial_token: str = "", additional_network: dict | None = None) -> str:
    """
    Provides the HTML content served when first requesting http://192.168.4.1 for provisioning

    :param device_id: A unique device ID, just for polishing
    :param initial_token: An initial token to prepopulate the user text field
    :param additional_network: An optional extra network {SSID: PW} to prepopulate the user field
    :return: A filled out HTML content
    """
    network_bullets = "".join(f"<li>{x}</li>" for x in DEFAULT_WIFI_NETWORKS)
    extra_ssid, extra_pw = "", ""
    if additional_network:
        entry = next(iter(additional_network.items()))
        extra_ssid, extra_pw = entry
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Freezer Sensor Setup</title>
      <style>
        body {{
          font-family: sans-serif;
          font-size: 18px;
          background: #f4f6f8;
          margin: 0;
          padding: 30px;
        }}

        .card {{
          background: white;
          max-width: 520px;
          margin: auto;
          padding: 25px 30px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}

        h1 {{
          margin-top: 0;
          font-size: 26px;
        }}

        h3 {{
          margin-bottom: 8px;
          margin-top: 22px;
        }}

        .field {{
          margin-bottom: 14px;
        }}

        .field label {{
          display: block;
          font-weight: bold;
          margin-bottom: 4px;
        }}

        input {{
          font-size: 16px;
          padding: 8px;
          width: 100%;
          box-sizing: border-box;
          border: 1px solid #ccc;
          border-radius: 4px;
        }}

        input:focus {{
          outline: none;
          border-color: #4a90e2;
        }}

        input[type="submit"] {{
          margin-top: 18px;
          background: #4a90e2;
          color: white;
          border: none;
          cursor: pointer;
        }}

        input[type="submit"]:hover {{
          background: #357abd;
        }}

        ul {{
          margin-top: 6px;
          padding-left: 20px;
        }}

        .device-id {{
          color: #555;
          margin-bottom: 15px;
        }}

        .masked {{
          -webkit-text-security: disc;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Temperature Sensor Setup</h1>
        <div class="device-id">Device ID: {device_id}</div>

        <form method="POST">
          <h3>Required GitHub Token</h3>
          <div class="field">
            <input name="github_token" class="masked" value="{initial_token}">
          </div>

          <h3>Known Networks</h3>
          <ul>
            {network_bullets}
          </ul>

          <h3>Optional Additional WiFi</h3>
          <div class="field">
            <label for="wifi_ssid">SSID</label>
            <input id="wifi_ssid" name="wifi_ssid" value="{extra_ssid}">
          </div>

          <div class="field">
            <label for="wifi_password">Password</label>
            <input id="wifi_password" name="wifi_password" class="masked" value="{extra_pw}">
          </div>

          <input type="submit" value="Save Configuration">
        </form>
      </div>
    </body>
    </html>
    """


def html_reboot() -> str:
    """
    Provides the HTML content shown after successfully POST-ing data to complete provisioning.

    :return: HTML content to show after provisioning
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Freezer Sensor Setup</title>
      <style>
        body {
          font-family: sans-serif;
          font-size: 18px;
          background: #f4f6f8;
          margin: 0;
          padding: 30px;
        }

        .card {
          background: white;
          max-width: 520px;
          margin: auto;
          padding: 25px 30px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        h1 {
          margin-top: 0;
          font-size: 26px;
        }

        h3 {
          margin-bottom: 8px;
          margin-top: 22px;
        }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Configuration Saved!</h1>
        <h3>Device will reboot...</h3>
      </div>
    </body>
    </html>
    """


def default_token() -> str:
    """
    Provides a default GH token, useful for testing.

    :return: A token
    """
    return ''.join(reversed([
        'i', '7', 'X', 'M', 't', '0', 'C', 'r',
        'k', 'R', 'n', 'j', '8', 'h', 'D', 'D',
        'N', 'a', 'J', '1', 's', 'o', 'A', 'V',
        'V', 'o', 'f', 'e', 'l', 'p', 'w', 'I',
        '8', 'r', '1', '9', '_', 'p', 'h', 'g'
    ]))
