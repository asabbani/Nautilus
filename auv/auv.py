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

        try:
            self.radio = Radio(RADIO_PATH)
        except:
            print("Radio device is not connected to AUV on RADIO_PATH")
        
        global BS_PING, AUV_PING
        BS_PING = str.encode(BS_PING)
        AUV_PING = str.encode(AUV_PING)


        self.main_loop()

    def main_loop(self):
        """ Main connection loop for the AUV. """
        while(True):
            if (self.radio is None or self.radio.isOpen() is False):
                try:
                    self.radio = Radio(RADIO_PATH)
                except:
                    pass
                finally:
                    if (self.radio is not None):
                        print("Radio device has been found!")
            else:
                try:
                    line = self.radio.readline()
                except:
                    self.radio.close()
                    self.radio = None
                    print("Radio is disconnected from pi!")
                    continue

                self.connected_to_bs = (line == BS_PING)

                if (self.connected_to_bs):
                    print("Connected to BS verified. Returning ping.")
                    self.radio.write(AUV_PING)
                    time.sleep(CONNECTION_WAIT_TIME)
                else:
                    print(line)
                    print("Not connected to BS.")
            
            time.sleep(THREAD_SLEEP_DELAY)


def main():
    """ Main function that is run upon execution of auv.py """
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
