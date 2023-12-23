import subprocess
import re

from SpotBox.Events import subscribe


class Shell:
    def __init__(self):
        def restartSpotifyd(*args): self.restartSpotifyd()

        subscribe("restart_spotifyd", restartSpotifyd)

    def restartSpotifyd(self):
        print("\x1b[0;37;41m" + "Trying to restart spotifyd daemon" + "\x1b[0m")
        process = subprocess.Popen(['systemctl', '--user', 'restart', 'spotifyd.service'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr != b'':
            raise Exception("Error {}".format(stderr))

    def isDeviceConnected(self, device_id):
        process = subprocess.Popen(['bluetoothctl', 'info', device_id],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if (stderr != b''):
            raise Exception("Error {}".format(stderr))

        stdout = stdout.decode("utf-8")
        lines = stdout.split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        return "Connected: yes" in lines

    # noinspection PyMethodMayBeStatic
    def connectDevice(self, device_id):
        process = subprocess.Popen(['bluetoothctl', 'connect', device_id],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return process.returncode == 0

    # noinspection PyMethodMayBeStatic
    def getPairedBluetoothDevices(self):
        process = subprocess.Popen(['bluetoothctl', 'paired-devices'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr != b'':
            raise Exception("Error {}".format(stderr))

        stdout = stdout.decode("utf-8")
        lines = stdout.split("\n")

        result = []
        mac_address_pattern = r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})"
        for line in lines:
            # Splitting the text based on the MAC address pattern
            parts = re.split(mac_address_pattern, stdout)
            cleaned_parts = [part.strip() for part in parts if part.strip()]
            result.append(cleaned_parts)

        return result

