'''
This class acts as the main functionality file for 
the Origin AUV. The "mind and brain" of the mission.
'''
# System imports
import os
import sys
import threading
import time

# Custom imports
from api import Radio
from api import IMU
from api import PressureSensor
from api import MotorController

RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
BS_PING = "BS_PING\n"
AUV_PING = "AUV_PING\n"
THREAD_SLEEP_DELAY = 0.3
CONNECTION_WAIT_TIME = 0.5


class AUV():
    """ Class for the AUV object. Acts as the main file for the AUV. """

    def __init__(self):
        """ Constructor for the AUV """

        self.radio = None
        self.mc = MotorController()
        self.connected_to_bs = False

        # Get all non-default callable methods in this class
        self.methods = [ m for m in dir(AUV) if not m.startswith('__')]

        try:
            self.radio = Radio(RADIO_PATH)
            print("Radio device has been found")
        except:
            print("Radio device is not connected to AUV on RADIO_PATH")

        global BS_PING, AUV_PING
        BS_PING = str.encode(BS_PING)
        AUV_PING = str.encode(AUV_PING)

        self.main_loop()
    
    def test_motor(self, motor):
        if motor is "LEFT":
            self.mc.test_left()
        elif motor is "RIGHT":
            self.mc.test_right()
        elif motor is "FRONT":
            self.mc.test_front()
        elif motor is "BACK":
            self.mc.test_back()

    def main_loop(self):
        """ Main connection loop for the AUV. """
        self.test_motor("LEFT")

        print("Starting main connection loop.")
        while(True):
            if (self.radio is None or self.radio.isOpen() is False):
                try:
                    self.radio = Radio(RADIO_PATH)
                    print("Radio device has been found!")
                except:
                    pass
            else:
                try:
                    line = self.radio.readline()
                except:
                    self.radio.close()
                    self.radio = None
                    print("Radio is disconnected from pi!")
                    continue

                # Save previous connection status
                self.before = self.connected_to_bs

                # Updated connection status
                self.connected_to_bs = (line == BS_PING)

                if (self.connected_to_bs):
                    # If there was a status change, print out updated
                    if (self.before is not self.connected_to_bs):
                        print("Connected to BS verified. Returning ping.")

                    self.radio.write(AUV_PING)
                    time.sleep(CONNECTION_WAIT_TIME)
                else:
                    # If there was a status change, print out updated
                    if (self.before is not self.connected_to_bs):
                        print("Connected to BS failed. Line read was: " + str(line))

            time.sleep(THREAD_SLEEP_DELAY)


def main():
    """ Main function that is run upon execution of auv.py """
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
