# I did not manage to get his running, yet. Whenever I connect Spotify to Raspotify, the later crashes with this message:

```
librespot[4031]: ALSA lib ../../../src/asound/bluealsa-pcm.c:1316:(_snd_pcm_bluealsa_open) Couldn't get BlueALSA PCM: PCM not found Dec 10 11:10:56 spotbox librespot[4031]: [2023-12-10T10:10:56Z ERROR librespot_playback::player] Audio Sink Error Connection Refused: <AlsaSink> Device bluealsa May be Invalid, Busy, or Already in Use, ALSA function 'snd_pcm_open' failed with error 'ENODEV: No such device'
```

There are some suggestions that this might be related to the DynamicUser Systemd configuration of raspotify - but I could not fix it 



# Essentials 
sudo apt-get install git vim checkinstall curl



# Setup bluetooth

sudo usermod -a -G bluetooth `whoami`
sudo usermod -a -G audio `whoami`

bluetoothctl
```
	Agent registered
	[bluetooth]# power on
	Changing power on succeeded
	[bluetooth]# pairable on
	Changing pairable on succeeded
	[bluetooth]# agent on
	Agent is already registered
	[bluetooth]# scan on
	Discovery started
	[CHG] Controller B8:27:EB:10:5B:B6 Discovering: yes
	[...]
	[NEW] Device E8:07:BF:EF:F0:A8 Maginon BHF35
	[bluetooth]# trust E8:07:BF:EF:F0:A8
	[bluetooth]# pair E8:07:BF:EF:F0:A8
	Attempting to pair with E8:07:BF:EF:F0:A8
	[CHG] Device E8:07:BF:EF:F0:A8 ServicesResolved: yes
	[CHG] Device E8:07:BF:EF:F0:A8 Paired: yes
	Pairing successful
```

40:C1:F6:D6:8C:8D

git clone https://github.com/bablokb/pi-btaudio.git
cd pi-btaudio
# Option 1: Build from source
tools/build-bluez-alsa
# Option 2: Install precompile package
# sudo dpkg -i deb/arkq-bluez-alsa_3.1.0-78_armhf.deb
sudo apt-get -f -y install
sudo tools/install

bluetoothctl devices

Enter the MAc that is output here to `/etc/asound.conf`

pcm.!default "bluealsa"
ctl.!default "bluealsa"
defaults.bluealsa.interface "hci0"
defaults.bluealsa.device "E8:07:BF:EF:F0:A8"
defaults.bluealsa.profile "a2dp"

    pcm.!default {
        type plug
        slave {
            pcm {
                type bluealsa
                device E8:07:BF:EF:F0:A8
                profile "a2dp"
            }
        }
        hint {
            show on
            description "Marshall MID"
        }
     }
    ctl.!default {
        type bluealsa
    }




# Raspotipy

`sudo apt-get -y install curl && curl -sL https://dtcooper.github.io/raspotify/install.sh | sh`

List devices

`librespot -d ?`

edit /etc/raspotify/conf
LIBRESPOT_DEVICE="bluealsa"


sysdefault:CARD=Headphones


## Change Dynamic User - DBUS error?
```
Modify the Service File: Look for a line that says DynamicUser=yes and either comment it out (by adding a # at the beginning of the line) or change it to DynamicUser=no.

Add a Static User: Instead of using a dynamic user, you can specify a static user for the service. Add these lines to the service file (or modify them if they already exist):

[Service]
User=your-username
Group=your-group

```

# Install Spotipy
pip3 install spotipy
