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
    
    # Make two dictionaries, one keyed on sensor name, and one keyed on the sensor
    # ID.
    data_n = {}
    data_i = {}
    for d in data_raw:
        data_n[d['name']] = d['rawValue']
        data_i[d['id']] = d['rawValue']
    for i in range(1, 16):
        nm = f'Temperature sensor {i}'
        id = f'00_0010_7E11_10_0100_{(i-1)*2:03}_2_0'
        print(nm, id, data_n[nm], data_i[id])

    nm = 'Irradiation sensor 16'
    id = '00_0010_7E11_10_0100_030_2_0'
    print(nm, id, data_n[nm], data_i[id])


    for i in range(1, 15):
        nm = f'Pump speed relay {i}'
        id = f'00_0010_7E11_10_0100_{75+i:03}_1_0'
        print(nm, id, data_n[nm], data_i[id])

    time.sleep(5)