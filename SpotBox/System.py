import os
import sys
import signal
import RPi.GPIO as GPIO
import time
from SpotBox.Events import post_event


def cleanup():
    print("cleaning up")
    post_event("status_running", False)
    GPIO.cleanup()


class System:
    def __init__(self, cache_path):
        self.cachePath = cache_path
        signal.signal(signal.SIGTERM, self.termHandler)

    # noinspection PyMethodMayBeStatic
    def termHandler(self, signal, frame):
        print("SIGTERM received, cleaning up")
        cleanup()
        sys.exit()

    def killPreviousInstances(self):
        pid_path = self.cachePath + "/pid"

        pid = ""
        try:
            with open(pid_path, 'r') as file:
                pid = file.read()
        except FileNotFoundError as e:
            pass

        try:
            if pid.isnumeric():
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)
                if os.path.isdir('/proc/{}'.format(pid)):
                    os.kill(int(pid), signal.SIGKILL)
                print("Terminated previously running instance")
        except ProcessLookupError as e:
            pass

        with open(pid_path, 'w') as file:
            file.write(str(os.getpid()))
