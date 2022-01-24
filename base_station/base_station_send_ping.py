# System imports
import serial
import time
import threading

# Custom imports
from api import Radio
from constants import RADIO_PATH, PING_SLEEP_DELAY, PING


class BaseStation_Send_Ping(threading.Thread):
    def run(self):
        """ Constructor for the AUV """
        self.radio = None

        try:
            self.radio = Radio(RADIO_PATH)
            print("Radio device has been found.")
        except:
            print("Radio device is not connected to AUV on RADIO_PATH.")

        self.main_loop()

    def main_loop(self):
        """ Main connection loop for the AUV. """
        global connected

        print("Starting main ping sending connection loop.")
        while True:
            time.sleep(PING_SLEEP_DELAY)

            if self.radio is None or self.radio.is_open() is False:
                print("TEST radio not connected")
                try:  # Try to connect to our devices.
                    self.radio = Radio(RADIO_PATH)
                    print("Radio device has been found!")
                except Exception as e:
                    print("Failed to connect to radio: " + str(e))

            else:
                try:
                    # Always send a connection verification packet
                    radio_lock.acquire()
                    self.radio.write(PING)
                    radio_lock.release()

                except Exception as e:
                    raise Exception("Error occured : " + str(e))
