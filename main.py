"""Script to periodically query sensor and relay readings from the resol-vbus
live JSON server, and then send those readings via LoRaWAN.
"""
import time
import os
import logging
from logging.handlers import RotatingFileHandler
from struct import pack, unpack

from e5lora import Board
import requests

import settings

def process_downlink(down_data: bytes):
    """Processes a downlink command sent to the LoRa E5 board.  'down_data' is a bytes
    object containing the data sent in the downlink.
    """
    if down_data[0] == 1:         # request to change data rate
        new_data_rate = down_data[1]
        if new_data_rate in (0, 1, 2, 3):
            lora_board.set_data_rate(new_data_rate) 

def get_val(ch_name, ch_id, name_dict, id_dict, default_val):
    """Returns a value from the 'name_dict' (priority) or 'id_dict' if
    the name does not existing in the 'name_dict'.  'ch_name' is the channel
    name, 'ch_id' is the channel ID.  If the channel does not exist in either
    dictionary, return 'default_val'
    """
    val = name_dict.get(
        ch_name,
        id_dict.get(
            ch_id,
            default_val
        )
    )
    return val

# Get the absolute path of the script
script_path = os.path.abspath(__file__)

# Get the directory name of the script
script_directory = os.path.dirname(script_path)

# Create a rotating file logger, which also logs to the console.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
handler = RotatingFileHandler(f'{script_directory}/../log/resol-to-lora.log', maxBytes=5000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info('Script started')

# make object to use the E5 LoRaWAN board
lora_board = Board(port=settings.E5_PORT, downlink_callback=process_downlink)

# Give time for Resol live server to start up and for E5 Lora Board to join.
time.sleep(10)

next_log_time = time.time()

while True:
    
    try:

        # just in case of a clock adjustment, make sure log time is within POST_INTERVAL
        # of now.
        next_log_time = min(next_log_time, time.time() + settings.POST_INTERVAL * 60.0)

        if time.time() >= next_log_time:
            # update time to log next
            next_log_time += settings.POST_INTERVAL * 60.0

            data_raw = requests.get(settings.RESOL_URL).json()
            
            # Make two dictionaries, one keyed on sensor name, and one keyed on the sensor
            # ID.
            data_n = {}
            data_i = {}
            for d in data_raw:
                data_n[d['name']] = d['rawValue']
                data_i[d['id']] = d['rawValue']

            # list to hold final values to send
            send_vals = []

            # get input channels 1 through 15, generally temperature values (deg C) but
            # could be switch statuses. Try the name dictionary first, and
            # then the ID dictionary if not in the name dictionary. If the sensor is
            # not present, use the value 888.8 which is what is used by Resol to indicate
            # no temperature value.
            for i in range(1, 16):
                nm = f'Temperature sensor {i}'
                id = f'00_0010_7E11_10_0100_{(i-1)*2:03}_2_0'
                val = get_val(nm, id, data_n, data_i, 888.8)
                # send the value as in integer number of tenths
                val = int(val * 10.0)
                send_vals.append(val)

            # Radiation sensor value, which is W / m2.  Send this as an integer
            # with no scaling.  Send 8888 if no sensor
            nm = 'Irradiation sensor 16'
            id = '00_0010_7E11_10_0100_030_2_0'
            val = int(get_val(nm, id, data_n, data_i, 8888))
            send_vals.append(val)

            # create a list of values to be sent in the uplink message
            up_list = [(7, 1)]       # message type 7
            # send each value as a 2-byte signed integer.  However, the send_uplink()
            # method needs unsigned values, thus the unpack(pack()) approach below.
            up_list += [(unpack('>H', pack('>h', val)), 2) for val in send_vals]

            # Relay output values. Use 0 if not present.
            # Create an integer where each bit is a relay status
            relay_val = 0
            mult = 1
            for i in range(1, 15):
                nm = f'Pump speed relay {i}'
                id = f'00_0010_7E11_10_0100_{75+i:03}_1_0'
                val = int(get_val(nm, id, data_n, data_i, 0))
                relay_val += mult * val
                mult *= 2
            # 2-byte integer is big enough to hold 14 relay values
            up_list.append( (relay_val, 2) )

            lora_board.send_uplink(up_list)
    
    except:
        logging.exception('Error collecting data.')

    time.sleep(1)
