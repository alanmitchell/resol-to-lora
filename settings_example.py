"""Settings file for the application.
Copy this file to a "settings.py" file in this directory, and then edit
that settings.py file as needed.
"""

# Minimum number of minutes between posting readings via LoRaWAN
POST_INTERVAL = 15.0

# ------------
# Unlikely to need to change the following settings

# URL of the Resol Live Server
RESOL_URL = 'http://127.0.0.1:3333/api/v1/live-data'

# Serial port where the SEEED E5 board is connected
E5_PORT = '/dev/ttyUSB0'
