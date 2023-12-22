import os
import time
from threading import Thread

import logging
import dbus
import pyudev
from dbus.mainloop.glib import DBusGMainLoop
from evdev import InputDevice, categorize, ecodes

from SpotBox.Events import post_event, subscribe


class BluetoothDevice:
    def __init__(self, config, spotify, shell):
        self.config = config
        self.spotify = spotify
        self.shell = shell

        subscribe('play_new_song', self.eventNewSong)

        self.thread = None

        # Watch for BT devices
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(self._bluetoothEventHandler,
                                dbus_interface="org.freedesktop.DBus.Properties",
                                signal_name="PropertiesChanged",
                                arg0="org.bluez.Device1",
                                path_keyword="path")

        self.monitorKeyEvents()
        self.watchKeyEvents()

        post_event("status_bluetooth", self.isDeviceConnected())
        self.connect()

    def eventNewSong(self, type, data, data2=None):
        self.connect()

    def connect(self):
        return self.shell.connectDevice(self.config.getBluetoothDevice())

    def isDeviceConnected(self):
        return self.shell.isDeviceConnected(self.config.getBluetoothDevice())

    def _watchKeyPresses(self):
        # https://talyian.github.io/ansicolors/
        device_path = self.config.getBluetoothDevicePath()
        # noinspection PyBroadException
        try:
            # use evtest to identify device & key code
            if os.path.exists(device_path):
                post_event("status_key", True)
                # Create an InputDevice object
                device = InputDevice(device_path)
                # print(f"Listening for events from {device.path}")
                # Loop to handle events
                for event in device.read_loop():
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        if key_event.keystate == key_event.key_down:
                            print("[Bluetooth Keys]Key detected", key_event.keycode)
                            if key_event.keycode == 'KEY_PLAYCD' or key_event.keycode == 'KEY_PAUSECD':
                                self.spotify.playPause()
            else:
                post_event("status_key", False)
        except Exception:
            logging.exception("Error reading bluetooth keys")
            post_event("status_key", False)

    def watchKeyEvents(self):
        if self.thread and self.thread.is_alive():
            print("Thread already running, returning")
            return
        self.thread = Thread(target=self._watchKeyPresses, name="evdev", daemon=True)
        self.thread.daemon = True
        self.thread.start()

    def monitorKeyEvents(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='input')

        def log_event(action, device):
            if device.device_node is None:
                return

            if self.config.getBluetoothDevicePath() in device.device_node:
                if device.action == 'add':
                    time.sleep(2)
                    self.watchKeyEvents()
                elif device.action == 'remove':
                    post_event("status_key", False)
                    pass

        observer = pyudev.MonitorObserver(monitor, log_event)
        observer.start()

    def _bluetoothEventHandler(self, interface, changed, invalidated, path):
        if not self.config.getBluetoothDevice().replace(":", "_") in path:
            return

        if "org.bluez.Device1" in interface:
            if "Connected" in changed:
                connected = changed["Connected"]
                if connected:
                    post_event("status_bluetooth", True)
                    self.watchKeyEvents()
                else:
                    post_event("status_bluetooth", False)
                    # self.watchDevice()

#    def watchDevice(self):
#        while (not self.isDeviceConnected()):
#            print("Waiting for bluetooth device")
#            time.sleep(3)
#
#
#
#    def _loopPoll(self):
#
#
#        device_path = self.config.getBluetoothDevicePath()
#        while not os.path.exists(device_path):
#            print("Bluetooth key device not yet found, keep looking")
#            time.sleep(2)
#        print("Bluetooth device found")
#
#        try:
#            # use evtest to identify device & key code
#            if os.path.exists(device_path):
#                # Create an InputDevice object
#                device = InputDevice(device_path)
#
#                print(f"Listening for events from {device.path}")
#
#                # Loop to handle events
#                for event in device.read_loop():
#                    print(".")
#                    if event.type == ecodes.EV_KEY:
#                        key_event = categorize(event)
#                        if key_event.keystate == key_event.key_down:
#                            print("Key detected", key_event.keycode)
#                            if key_event.keycode == 'KEY_PLAYCD' or key_event.keycode == 'KEY_PAUSECD':
#                                self.spotify.playPause()
#            else:
#                print("\x1b[0;30;43mDid not register hotkeys as BT input device was not found\x1b[0m")
#
#        except OSError:
#            print("\x1b[0;30;43mConnection to BT input device lost\x1b[0m")
