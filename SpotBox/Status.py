from SpotBox.Events import subscribe, post_event
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


class Status:
    status_map = {
        # "status_key": 2,
        "status_bluetooth": 26,  # blue LED
        "status_playing": 4,  #
        "status_running": 2
    }

    def __init__(self):
        subscribe('status_key', self.setStatus)
        subscribe('status_bluetooth', self.setStatus)
        subscribe('status_playing', self.setStatus)
        subscribe('status_running', self.setStatus)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for k, v in self.status_map.items():
            GPIO.setup(v, GPIO.OUT)
            setattr(self, k, False)

        post_event("status_running", True)

    def setStatus(self, type, data, data2=None):
        if data != getattr(self, type, data):
            print("Status {} changed to {}".format(type, str(data)))

        if type == "status_key" and data == False:
            print("\x1b[0;30;43m[Bluetooth Keys] Input device was not found\x1b[0m")
        elif type == "status_key" and data == True:
            print("\x1b[0;30;42m[Bluetooth Keys] Found - Now watching for key events\x1b[0m")
        elif type == "status_bluetooth" and data == True:
            print("\x1b[0;30;42m[Bluetooth] Connected\x1b[0m")
        elif type == "status_bluetooth" and data == False:
            print("\x1b[0;30;43m[Bluetooth] Connection lost\x1b[0m")

        setattr(self, type, data)

        self.updateLEDs()

    def updateLEDs(self):
        for status, pin in self.status_map.items():
            GPIO.output(pin, GPIO.HIGH) if getattr(self, status) else GPIO.output(pin, GPIO.LOW)

    def printAllStatus(self):
        for k, v in vars(self).items():
            print(str(k) + ": " + str(v))
