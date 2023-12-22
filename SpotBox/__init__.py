from .Spotify import Spotify
from .Shell import Shell
from .Config import Config
from .RFID import RFID
from .System import System
from .BluetoothDevice import BluetoothDevice
from .Status import Status
from .Buttons import Buttons
from .Shutdown import Shutdown

import logging
logging.basicConfig(filename='spotbox.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
