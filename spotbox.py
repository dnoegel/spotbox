#!/usr/bin/env python3
import logging
import os

import RPi.GPIO as GPIO
from gi.repository import GLib as GLib

GPIO.setmode(GPIO.BCM)

from SpotBox import Spotify
from SpotBox import Shell
from SpotBox import Config
from SpotBox import RFID
from SpotBox import BluetoothDevice
from SpotBox import System
from SpotBox import Status
from SpotBox import Buttons
from SpotBox.Xdg import xdg_config_home, xdg_cache_home
from SpotBox.Events import post_event
from SpotBox import Shutdown

import urllib.request, json
import re
import time


def readAlbumMapping(url):
    print(url + "?randomHash=" + str(time.time()))
    with urllib.request.urlopen(url + "?randomHash=" + str(time.time())) as response:
        data = response.read().decode('utf-8')

    data = re.sub(r"#.*?\\n", "", data)

    data = json.loads(data)
    data = json.loads(data)
    print("{} albums found".format(len(data)))
    return data


def run():
    cache_path = os.path.join(xdg_cache_home(), "spotbox")
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    system = System(cache_path)
    system.killPreviousInstances()

    config = Config(xdg_config_home())
    shell = Shell()
    status = Status()

    spotify = Spotify(config, cache_path)
    shutdown = Shutdown(spotify, config.getShutdownAfterMinutes())
    buttons = Buttons(spotify)

    rfid = RFID(
        spotify,
        config.getRfidReadDelay(),
        readAlbumMapping(config.getAlbumUrl())
    )

    bluetooth_device = BluetoothDevice(config, spotify, shell)

    shell.connectDevice(config.getBluetoothDevice())

    rfid.watchRFID()

    # spotify.playSomethingNew("spotify:playlist:37i9dQZF1Fa1IIVtEpGUcU")
    # spotify.shuffle(True)
    # spotify.next()

    # spotify.playSomethingNew("spotify:album:3Q9wXhEAX7NYCPP0hxIuDz")

    post_event("status_running", True)

    print("Spotbox started")

    loop = GLib.MainLoop()
    loop.run()


if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        run()
    except Exception as e:
        logging.exception("Error")
        print(e)
        pass
    #
    # from SpotBox.System import cleanup
    # cleanup()
    # print(traceback.format_exc())
    # sys.exit()
