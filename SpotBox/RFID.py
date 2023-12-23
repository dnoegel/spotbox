from SpotBox.Events import post_event
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from threading import Thread
import time
import logging

GPIO.setmode(GPIO.BCM)

RFID_GPIO = 22


def activateRFID():
    GPIO.output(RFID_GPIO, GPIO.HIGH)


def deactivateRFID():
    GPIO.output(RFID_GPIO, GPIO.LOW)



class RFID:
    map = {}

    lastSeenTag = None
    lastSeenTime = 0
    thread = None

    def __init__(self, spotify, read_delay, data):
        self.reader = SimpleMFRC522()
        self.spotify = spotify
        self.readDelay = int(read_delay)

        self.map = data

        GPIO.setup(RFID_GPIO, GPIO.OUT)
        activateRFID()

    def handleRFIDTag(self, id):
        id = str(id)
        logging.info("RFID detected: {}".format(id))

        if self.lastSeenTag == id and self.lastSeenTime + 5 >= time.time():
            logging.debug("Skipping RFID, same as before")
            self.lastSeenTime = time.time()
            return

        self.lastSeenTime = time.time()

        if id in self.map:
            post_event("play_new_song", self.map[id])
            self.lastSeenTime = time.time()
            self.lastSeenTag = id

    def watchRFID(self):
        self.thread = Thread(target=self._loop, name="rfid", daemon=True)
        self.thread.daemon = True
        self.thread.start()

    def _loop(self):
        """"
             The reference implementation mentioned for the SimpleMFRC522 library will call the read() method that looks like this:

               def read(self):
                   id, text = self.read_no_block()
                   while not id:
                       id, text = self.read_no_block()
                   return id, text

               This will basically poll the read_no_block() continuously and in my case utilized a whole core.
               By calling the read_no_block() method directly and sleeping a second after each iteration, the core usage
               can be reduced significantly.

               There seems to be a hack for the used library here: https://github.com/mxgxw/MFRC522-python/issues/17#issuecomment-269629633
               Furthermore this library seems to support IRQ/interrupt based card reading: https://github.com/ondryaso/pi-rc522

        """

        read_delay = self.readDelay
        while True:
            try:
                id, text = self.reader.read_no_block()
                if id is None:
                    time.sleep(read_delay)
                    continue

                print("RFID detected: " + str(id))

                self.handleRFIDTag(id)
                time.sleep(3)

                # print(text)
            except Exception as e:
                logging.exception("Error reading the RFID")
            finally:
                pass
