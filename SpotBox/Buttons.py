
import RPi.GPIO as GPIO
from SpotBox.Spotify import Spotify
import logging

GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class Buttons:
    def __init__(self, spotify: Spotify):
        self.spotify = spotify

        self._registerButtonForShutdown()

    def _registerButtonForShutdown(self):
        GPIO.add_event_detect(16, GPIO.BOTH, callback=self.callbackButtonEvent, bouncetime=200)
        GPIO.add_event_detect(20, GPIO.BOTH, callback=self.callbackButtonEvent, bouncetime=200)
        GPIO.add_event_detect(21, GPIO.BOTH, callback=self.callbackButtonEvent, bouncetime=200)

    def callbackButtonEvent(self, channel):
        if GPIO.input(channel) == 0:
            logging.info("Button pressed: " + "Prev" if channel == 16 else "Play/Pause" if channel == 20 else "Next")

        if GPIO.input(16) == 0:
            self.spotify.previous()
        if GPIO.input(20) == 0:
            self.spotify.playPause()
        if GPIO.input(21) == 0:
            self.spotify.next()
