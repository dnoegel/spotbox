import configparser
import os


class Config:

    def __init__(self, home):
        self.configparser = configparser.ConfigParser()
        self.configparser.read(os.path.join(home, 'spotbox/spotbox.conf'))

    def getBluetoothDevice(self):
        return self.configparser["Bluetooth"]["macAddress"]

    def getBluetoothDevicePath(self):
        return self.configparser["Bluetooth"].get("devicePath", None)

    def getRfidReadDelay(self):
        return int(self.configparser["Spotbox"].get("rfidReadDelaySecond", "1"))

    def getSpotifyDeviceId(self):
        return self.configparser["Spotify"]["deviceId"]

    def getClientId(self):
        return self.configparser["Spotify"]["clientId"]

    def getClientSecret(self):
        return self.configparser["Spotify"]["clientSecret"]

    def getRedirectUri(self):
        return self.configparser["Spotify"]["redirectUri"]

    def getAlbumUrl(self):
        return self.configparser["Spotbox"]["albumUrl"]

    def getShutdownAfterMinutes(self):
        return int(self.configparser["Spotbox"].get("shutdown_after_minutes", 30))
