import spotipy
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
import re
import time
from SpotBox.Events import post_event, subscribe
import logging

track_uri = 'spotify:track:1or6RDFkPMi3u4KM2LUBr3'
album_uri = 'spotify:album:3Q9wXhEAX7NYCPP0hxIuDz'
playlist_uri = 'spotify:playlist:3Q9wXhEAX7NYCPP0hxIuDz'


class Spotify:
    devices = []

    def __init__(self, config, cache_path):
        self.config = config
        self.device_id = config.getSpotifyDeviceId()

        subscribe('play_new_song', self.eventNewSong)
        subscribe('status_bluetooth', self.eventStatusBluetoothChanged)

        auth_manager = SpotifyOAuth(
            cache_handler=CacheFileHandler(cache_path=cache_path + "/token"),
            client_id=config.getClientId(),
            client_secret=config.getClientSecret(),
            redirect_uri=config.getRedirectUri(),
            scope="user-read-playback-state user-library-read streaming app-remote-control user-modify-playback-state",
            open_browser=False
        )
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

        # print(auth_manager.get_access_token())
        # exit()

        self.get_devices()
        if not self.device_id in self.devices:
            print("\x1b[0;37;41m" + "Device {} not found".format(self.device_id) + "\x1b[0m")
            post_event("restart_spotifyd", None)
            time.sleep(3)
            self.get_devices()
            if not self.device_id in self.devices:
                print("\x1b[0;37;41m" + "Still cannot find spotify id" + "\x1b[0m")
                exit(1)

    def eventStatusBluetoothChanged(self, type, data, data2=None):
        if data == False:
            self.pause()

    def eventNewSong(self, type, data, data2=None):
        self.playSomethingNew(data)

    def shuffle(self, shuffle):
        self.spotify.shuffle(shuffle, self.device_id)

    def get_devices(self):
        devices = self.spotify.devices()
        device_id = None
        for device in devices['devices']:
            self.devices.append(device['id'])
            print(device["id"] + ": ", device["name"])

    def isPlaying(self):
        if self.spotify.current_playback() is None:
            return False
        return self.spotify.current_playback()['is_playing']

    def playPause(self):
        if self.isPlaying():
            self.pause()
        else:
            self.play()

    # noinspection PyMethodMayBeStatic
    def convertToSpotifyUrl(self, url):
        if url.startswith("spotify:"):
            return url

        pattern = r"/(track|album|artist|playlist)/([0-9A-Za-z]+)"

        match = re.search(pattern, url)
        if match:
            return f"spotify:{match.group(1)}:{match.group(2)}"
        else:
            logging.error("Invalid URL: " + url)
            return False

    def playSomethingNew(self, album_uri):
        album_uri = self.convertToSpotifyUrl(album_uri)
        print(album_uri)
        if album_uri == False: return

        print("Playing: " + album_uri)

        self.spotify.start_playback(device_id=self.device_id, context_uri=album_uri)
        post_event("status_playing", True)

    def play(self):
        self.spotify.start_playback(device_id=self.device_id)
        post_event("status_playing", True)

    def pause(self):
        self.spotify.pause_playback(self.device_id)
        post_event("status_playing", False)

    def next(self):
        self.spotify.next_track(self.device_id)

    def previous(self):
        self.spotify.previous_track(self.device_id)
