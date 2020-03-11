""" This class manages the serial connection between the
AUV and Base Station along with sending controller
commands. """

import sys
import os

# System imports
import serial
import time
import math
import argparse
import threading
from queue import Queue

# Custom imports
from api import Radio
from api import Joystick
from api import NavController
from api import GPS
from gui import Main

# Constants
SPEED_CALIBRATION = 10
NO_CALIBRATION = 9
CONNECTION_WAIT_TIME = 3
THREAD_SLEEP_DELAY = 0.3
IS_MANUAL = True
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
PING = b'PING\n'


class BaseStation(threading.Thread):
    """ Base station class that acts as the brain for the entire base station. """

    def __init__(self, in_q=None, out_q=None):
        """ Initialize Serial Port and Class Variables
        debug: debugging flag """

        # Call super-class constructor
        threading.Thread.__init__(self)

        # Instance variables
        self.radio = None
        self.joy = None
        self.connected_to_auv = False
        self.nav_controller = None
        self.gps = None  # create the thread
        self.in_q = in_q
        self.out_q = out_q

        # Get all non-default callable methods in this class
        self.methods = [m for m in dir(BaseStation) if not m.startswith(
            '__') and not m.startswith('_')]

        # Try to assign our radio object
        try:
            self.radio = Radio(RADIO_PATH)
            self.log("Successfully found radio device on RADIO_PATH.")
        except:
            self.log(
                "Warning: Cannot find radio device. Ensure RADIO_PATH is correct.")

        print(self.methods)
        # Try to assign our GPS object connection to GPSD
        try:
            self.gps = GPS()
            self.log("Successfully connected to gpsd socket.")
        except:
            self.log("Warning: Cannot find a gpsd socket.")

    def calibrate_controller(self):
        """ Instantiates a new Xbox Controller Instance and NavigationController """
        # Construct joystick and check that the driver/controller are working.
        self.joy = None
        self.main.log("Attempting to connect xbox controller")
        while self.joy is None:
            self.main.update()
            try:
                self.joy = xbox.Joystick()
            except Exception as e:
                continue
        self.main.log("Xbox controller is connected.")

        # Instantiate New NavController With Joystick
        self.nav_controller = NavController(
            self.joy, self.button_cb, self.debug)

        self.main.log("Controller is connected.")

    def check_tasks(self):
        while not self.in_q.empty():
            task = "self." + self.in_q.get()
            # Try to evaluate the task in the in_q.
            print(task)  # TODO debug
            try:
                eval(task)
                print("success")
            except:
                print("Failed to evaluate in_q task: ", task)

    def test_motor(self, motor):
        """ Attempts to send the AUV a signal to test a given motor. """
        if not self.connected_to_auv:
            self.log("Cannot test " + motor +
                     " motor(s) because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("test_motor('" + motor + "')\n"))
            self.log('Sending task: test_motor("' + motor + '")')

    def abort_mission(self):
        """ Attempts to abort the mission for the AUV."""

        if not self.connected_to_auv:
            self.log(
                "Cannot abort mission because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("abort_mission()\n"))
            self.log("Sending task: abort_mission()")

    def start_mission(self, mission):
        """  Attempts to start a mission and send to AUV. """

        if (self.connected_to_auv is False):
            self.log("Cannot start mission: " + mission +
                     " because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("start_mission('" + mission + "')\n"))
            self.log('Sending task: start_mission("' + mission + '")')

    def run(self):
        """ Main threaded loop for the base station. """

        # Begin our main loop for this thread.
        while True:
            self.check_tasks()

            # This executes if we never had a radio object, or it got disconnected.
            if self.radio is None or not self.radio.is_open():

                # This executes if we HAD a radio object, but it got disconnected.
                if self.radio is not None and not self.radio.is_open():
                    self.log("Radio device has been disconnected.")
                    self.radio.close()

                # Try to assign us a new Radio object
                try:
                    self.radio = Radio(RADIO_PATH)
                    self.log(
                        "Radio device has been found on RADIO_PATH.")
                except:
                    pass

            # If we have a Radio object device, but we aren't connected to the AUV
            else:
                # Try to read line from radio.
                try:
                    self.radio.write(PING)
                    line = self.radio.readline()
                except:
                    self.radio.close()
                    self.radio = None
                    self.log("Radio device has been disconnected.")
                    continue

                self.before = self.connected_to_auv

                self.connected_to_auv = (line == PING)

                if self.connected_to_auv:
                    if self.before is False:
                        self.out_q.put("set_connection(True)")
                        self.log("Connection to AUV verified.")

                elif len(line) > 0:
                    # Line is greater than 0, but not equal to the AUV_PING
                    # which means a possible command was found.
                    message = line.decode('utf-8').replace("\n", "")

                    # Check if message is a possible python function
                    if len(message) > 2 and "(" in message and ")" in message:
                        # Get possible function name
                        possible_func_name = message[0:message.find("(")]
                        if possible_func_name in self.methods:
                            self.log("Received command from AUV: " + message)
                            try:
                                # Attempt to evaluate command. => Uses Vertical Pole '|' as delimiter
                                eval(message)
                                self.log(
                                    "Successfully evaluated command: " + message)
                            except:
                                # Send verification of command back to base station.
                                self.log("Evaluation of command  " +
                                         message + "  failed.")

                elif self.before:
                    # We are NOT connected to AUV, but we previously ('before') were. Status has changed to failed.
                    self.out_q.put("set_connection(False)")
                    self.log("Connection verification to AUV failed.")

            time.sleep(THREAD_SLEEP_DELAY)

    def log(self, message):
        self.out_q.put("log('" + str(message) + "')")

    def close(self):
        os._exit(1)  # => Force-exit the process immediately.


def main():
    """ Main method responsible for developing the main objects used during runtime
    like the BaseStation and Main objects. """

    # Define Queue data structures in order to communicate between threads.
    to_GUI = Queue()
    to_BS = Queue()

    # Create a BS (base station) and GUI object thread.
    threaded_bs = BaseStation(to_BS, to_GUI)
    threaded_bs.start()

    # Create main GUI object
    gui = Main(to_GUI, to_BS)


if __name__ == '__main__':
    main()
