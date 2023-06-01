"""Script to periodically query sensor and relay readings from the resol-vbus
live JSON server, and then send those readings via LoRaWAN.
"""
import time

import e5lora
import requests

import settings

# Give time for Resol live server to start up.
time.sleep(5)

while True:

    data_raw = requests.get(settings.RESOL_URL).json()
    
    # Key the data on sensor name
    data = {}
    for d in data_raw:
        data[d['name']] = d['rawValue']
    for i in range(1, 16):
        nm = f'Temperature sensor {i}'
        print(nm, data[nm])

    for i in range(1, 15):
        nm = f'Pump speed relay {i}'
        print(nm, data[nm])

    time.sleep(5)