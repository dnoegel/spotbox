import logging
import subprocess
import threading
import time

import RPi.GPIO as GPIO

from SpotBox.RFID import deactivateRFID

# Set up GPIO using BCM numbering
GPIO.setup(3, GPIO.IN)


class Shutdown:
    def __init__(self, spotify, shutdown_after_minutes):
        shutdown_after_seconds = shutdown_after_minutes * 60
        self.shutdownCheckInterval = 5 * 60
        self.shutdownCheckCounter = shutdown_after_seconds / self.shutdownCheckInterval

        self.spotify = spotify
        self.notPlayingCounter = 0

        self._buttonPressStartTime = None
        self._registerButtonForShutdown()

        self._startTimer()

    def _registerButtonForShutdown(self):
        GPIO.add_event_detect(3, GPIO.BOTH, callback=self.callbackShuttdownButtonEvent, bouncetime=200)

    def _checkPlaying(self):
        if not self.spotify.isPlaying():
            print("not playing")
            self.notPlayingCounter += 1

        if self.notPlayingCounter >= self.shutdownCheckCounter:
            print("Shutdown")
            self._shutdown()
            return

        self._startTimer()

    def callbackShuttdownButtonEvent(self, channel):
        if GPIO.input(3) == 0:
            self._buttonPressStartTime = time.time()
        else:
            if self._buttonPressStartTime is not None:
                elapsed = time.time() - self._buttonPressStartTime
                if elapsed > 2:
                    self._shutdown("Shutdown button pressed")
                self._buttonPressStartTime = None

    def _startTimer(self):
        self.checkTimer = threading.Timer(self.shutdownCheckInterval, self._checkPlaying)
        self.checkTimer.daemon = True
        self.checkTimer.start()

    # noinspection PyMethodMayBeStatic
    def _shutdown(self, reason=None):
        reason = 'Shutting down due to inactivity' if reason is None else 'Shutting down: ' + reason
        print(reason)
        logging.warning(reason)

        deactivateRFID()

        process = subprocess.Popen(['sudo', 'shutdown', '-Ph', 'now'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        logging.info(stdout)
        logging.info(stderr)
