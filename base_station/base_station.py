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
THREAD_SLEEP_DELAY = 0.1  # Since we are the slave to AUV, we must run faster.
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
PING = b'PING\n'
CONNECTION_TIMEOUT = 4

# AUV Constants (these are also in auv.py)
MAX_AUV_SPEED = 100
MAX_TURN_SPEED = 50


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
        self.manual_mode = True
        self.time_since_last_ping = 0.0

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

        # Try to connect our Xbox 360 controller.
        try:
            self.joy = Joystick()
            if (joy.connected()):
                self.log("Successfuly found Xbox 360 controller.")
                self.nav_controller = NavController(self.joy)
                self.log(
                    "Successfully created a Navigation with Controller object.")
        except:
            self.log("Warning: Cannot find Xbox 360 controller.")

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
        """ This checks all of the tasks (given from the GUI thread) in our in_q, and evaluates them. """

        while not self.in_q.empty():
            task = "self." + self.in_q.get()
            # Try to evaluate the task in the in_q.
            try:
                eval(task)
            except Exception as e:
                print("Failed to evaluate in_q task: ", task)
                print("\t Error received was: ", str(e))

    def auv_data(self, heading, temperature):
        self.heading = heading
        self.temperature = temperature
        self.out_q.put("set_heading("+str(heading)+")")
        self.out_q.put("set_temperature("+str(temperature)+")")

    def test_motor(self, motor):
        """ Attempts to send the AUV a signal to test a given motor. """

        if not self.connected_to_auv:
            self.log("Cannot test " + motor +
                     " motor(s) because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode('test_motor("' + motor + '")\n'))
            self.log('Sending task: test_motor("' + motor + '")')

    def abort_mission(self):
        """ Attempts to abort the mission for the AUV."""
        if not self.connected_to_auv:
            self.log(
                "Cannot abort mission because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("abort_mission()\n"))
            self.log("Sending task: abort_mission()")
            self.manual_mode = True

    def mission_failed(self):
        """ Mission return failure from AUV. """
        self.manual_mode = True
        self.out_q.put("set_vehicle(True)")
        self.log("Enforced switch to manual mode.")

        self.log("The current mission has failed.")

    def start_mission(self, mission):
        """  Attempts to start a mission and send to AUV. """

        if self.connected_to_auv is False:
            self.log("Cannot start mission: " + str(mission) +
                     " because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode(
                "start_mission(" + str(mission) + ")\n"))
            self.log('Sending task: start_mission(' + str(mission) + ')')

    def run(self):
        """ Main threaded loop for the base station. """
        self.log("Running radio connection loop to locate AUV...")
        # Begin our main loop for this thread.
        while True:
            self.check_tasks()

            # Always try to update connection status
            if time.time() - self.time_since_last_ping > CONNECTION_TIMEOUT:
                # We are NOT connected to AUV, but we previously ('before') were. Status has changed to failed.
                if self.connected_to_auv is True:
                    self.out_q.put("set_connection(False)")
                    self.log("Lost connection to AUV.")
                    self.connected_to_auv = False

            # Check if we have an Xbox controller
            if self.joy is None:
                try:
                    self.joy = Joystick()
                    self.nav_controller = NavController(self.joy)
                except:
                    pass

            elif not self.joy.connected():
                self.log("Xbox controller has been disconnected.")
                self.joy = None
                self.nav_controller = None

            # This executes if we never had a radio object, or it got disconnected.
            if self.radio is None or not os.path.exists(RADIO_PATH):

                # This executes if we HAD a radio object, but it got disconnected.
                if self.radio is not None and not os.path.exists(RADIO_PATH):
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

                    # This is where secured/synchronous code should go.
                    if self.connected_to_auv and self.manual_mode:
                        if self.joy is not None and self.joy.connected() and self.nav_controller is not None:
                            self.nav_controller.handle()
                            self.radio.write(
                                "xbox(" + self.nav_controller.get_data())
                    # Read ALL lines stored in buffer (probably around 2-3 commands)
                    lines = self.radio.readlines()
                    self.radio.flush()

                    for line in lines:
                        if line == PING:
                            self.time_since_last_ping = time.time()
                            if self.connected_to_auv is False:
                                self.log("Connection to AUV verified.")
                                self.out_q.put("set_connection(True)")
                                self.connected_to_auv = True

                        elif len(line) > 0:
                            # Line is greater than 0, but not equal to the AUV_PING
                            # which means a possible command was found.
                            message = line.decode('utf-8').replace("\n", "")

                            # Check if message is a possible python function
                            if len(message) > 2 and "(" in message and ")" in message:
                                # Get possible function name
                                possible_func_name = message[0:message.find(
                                    "(")]
                                if possible_func_name in self.methods:
                                    if possible_func_name != "auv_data" and possible_func_name != "log":
                                        self.log(
                                            "Received command from AUV: " + message)
                                    # Put task received into our in_q to be processed later.
                                    self.in_q.put(message)

                except:
                    self.radio.close()
                    self.radio = None
                    self.log("Radio device has been disconnected.")
                    continue

            time.sleep(THREAD_SLEEP_DELAY)

    def log(self, message):
        """ Logs the message to the GUI console by putting the function into the output-queue. """
        self.out_q.put("log('" + message + "')")

    def mission_started(self, index):
        """ When AUV sends mission started, switch to mission mode """
        if index == 0:  # Echo location mission.
            self.manual_mode = False
            self.out_q.put("set_vehicle(False)")
            self.log("Switched to autonomous mode.")

        self.log("Successfully started mission " + str(index))

    def close(self):
        """ Function that is executed upon the closure of the GUI (passed from input-queue). """
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
