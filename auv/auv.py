'''
This class acts as the main functionality file for 
the Origin AUV. The "mind and brain" of the mission.
'''
# System imports
import os
import sys
import threading

# Custom imports
from api import Radio
from api import IMU
from api import PressureSensor
from api import MotorController

RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'


class AUV():
    """ Class for the AUV object. Acts as the main file for the AUV. """

    def __init__(self):
        """ Constructor for the AUV """

        self.radio = None
        self.mc = MotorController()

        try:
            self.radio = Radio(RADIO_PATH)
        except:
            print("Radio device is not connected to AUV on RADIO_PATH")

        self.main_loop()

    def main_loop():
        """ Main connection loop for the AUV. """
        pass


def main():
    """ Main function that is run upon execution of auv.py """
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
