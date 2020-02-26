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
BS_PING = 'BS_PING\n'
AUV_PING = 'AUV_PING\n'
DONE = "DONE\n"


class BaseStation(threading.Thread):
    """ Base station class that acts as the brain for the entire base station. """

    def __init__(self, debug=False, in_q=None, out_q=None):
        """ Initialize Serial Port and Class Variables
        debug: debugging flag """

        # Call super-class constructor
        threading.Thread.__init__(self)

        # Instance variables
        self.radio = None
        self.data_packet = []
        self.joy = None
        self.connected_to_auv = False
        self.navController = None
        self.debug = debug
        self.cal_flag = NO_CALIBRATION
        self.radio_timer = []
        self.gps = None  # create the thread
        self.ballast_depth = 0
        self.button_cb = {'MAN': self.manual_control, 'BAL': self.ballast}
        self.in_q = in_q
        self.out_q = out_q

        # Convert out PING unicode strings to bytes.
        global BS_PING, AUV_PING
        BS_PING = str.encode(BS_PING)
        AUV_PING = str.encode(AUV_PING)

        # Try to assign our radio object
        try:
            self.radio = Radio(RADIO_PATH)
        except:
            self.log(
                "Warning: Cannot find radio device. Ensure RADIO_PATH is correct.")

        # Try to assign our GPS object connection to GPSD
        try:
            self.gps = GPS()
        except:
            self.log("Warning: Cannot find a gpsd socket.")

    def set_main(self, Main):
        self.main = Main

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
        self.main.log("Xbox controller is connected")

        # Instantiate New NavController With Joystick
        self.navController = NavController(
            self.joy, self.button_cb, self.debug)

        self.main.log("Controller is connected")

    def calibrate_communication(self):
        """ Ensure communication between AUV and Base Station """

        # Flush the serial connection.
        self.radio.flush()

        self.main.log("Attempting to establish connection to AUV...")
        self.main.update()

        # Wait until connection is established.
        while not self.connected_to_auv:
            # Send Calibration Signal To AUV
            #            if self.radio.write(CAL) == -1:
         #               self.main.log("Radios have been physically disconnected. Check USB connection.")

            self.radio.write(CAL)
            # Attempt to read from radio
            line = self.radio.readline()
            print("line read is: ", line)
            # If we got an error (returned 0)
  #          if line == -1:
            # self.main.log("Radios have been physically disconnected. Check USB connection.")
   #         else:
            self.connected_to_auv = (line == CAL) or (line == REC)

            if not self.connected_to_auv:
                self.main.log("Connection timed out, trying again...")

        self.radio.flush()
        self.main.log("Connection established with AUV.")
        self.main.comms_status_string.set("Comms Status: Connected")

    def check_tasks(self):
        while(self.in_q.empty() is False):
            task = self.in_q.get()
            print("Found task: " + task)
            eval("self." + task)

    def test_motor(self, motor):
        """ Attempts to send the AUV a signal to test a given motor. """
        if (self.connected_to_auv is False):
            self.log("Cannot test " + motor +
                     " motor(s) because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("test_motor '" + motor + "'\n"))
            self.log("Sending task: test_motor \"" + motor + "\"")

    def abort_mission(self):
        """ Attempts to abort the mission for the AUV."""

        if (self.connected_to_auv is False):
            self.log(
                "Cannot abort mission because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("abort_mission\n"))
            self.log("Sending task: abort_mission")

    def start_mission(self, mission):
        """  Attempts to start a mission and send to AUV. """

        if (self.connected_to_auv is False):
            self.log("Cannot start mission: " + mission +
                     " because there is no connection to the AUV.")
        else:
            self.radio.write(str.encode("start_mission '" + mission + "'\n"))
            self.log("Sending task: start_mission \"" + mission + "\"")

    def run(self):
        """ Main threaded loop for the base station. """

        # Begin our main loop for this thread.
        while True:
            self.check_tasks()

            # If we cannot find a radio device, or the object we have is closed.
            if (self.radio is None or self.radio.isOpen() is False):

                # If we have a radio object, but no serial connnect (disconnected after).
                if(self.radio is not None and self.radio.isOpen() is False):
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
                # Add newline character to distinguish packet
                self.radio.write(BS_PING)

                # Try to read line from radio.
                try:
                    line = self.radio.readline()
                except:
                    self.radio.close()
                    self.radio = None
                    self.log("Radio has been disconnected from computer.")
                    continue

                self.before = self.connected_to_auv

                self.connected_to_auv = (line == AUV_PING)

                if (self.connected_to_auv):
                    if (self.before is not self.connected_to_auv):
                        self.out_q.put("set_connection(True)")
                        self.log("Connection to AUV verified.")
                else:
                    if (self.before is not self.connected_to_auv):
                        self.out_q.put("set_connection(False)")
                        self.log("Connection to AUV failed.")

            time.sleep(THREAD_SLEEP_DELAY)

         # try:
         # Start Control Loop
#        self.radio.write(chr(SPEED_CALIBRATION))
        # self.gpsp.start()
#        curr_time = time.time()

        # while self.connected_to_auv:
#        while True:
          #  self.main.log("GPS: {}".format(self.gps.gpsd.fix.latitude))
#            self.navController.handle()
#             #Get pa0cket
#             self.data_packet = self.navController.getPacket()
#             self.data_packet = self.data_packet + chr(self.cal_flag) + '\n'
#             print("Data packet: ", self.data_packet)

#             if IS_MANUAL:
#                 delta_time = time.time() - curr_time
#                 self.radio_timer.append( delta_time )
#                # print("writing json data of: " , json.dumps(self.test_dict) )
#                 self.radio.write(self.data_packet)
#                 #self.radio.write(json.dumps(self.test_dict) + '\n')
#                 curr_time = time.time()

#             #else:
#                 # Send packet for autonomous movement; Aborting mission, where is home, where is waypoint, start ballast, switch back to manual
#                 #auto_packet = [ isAborting, home_wp, wp_dest, ballast, is_Manual ]

#             #Reset motor calibration
#             self.cal_flag = NO_CALIBRATION
#             if ord(self.data_packet[3]) == 1:
#                 self.main.log("Entering ballast state.")
#                 self.enter_ballast_state()
#                 self.main.log("Finished ballasting.")
#                 self.radio.write(chr(SPEED_CALIBRATION))

#             # Await response from AUV.
#             if self.radio.readline() != 'REC\n':

#                 self.connected_to_auv = False

#                 print("WARNING - AUV disconnected. Attempting to reconnect.")

#                 self.calibrate_communication()

# #                data = self.radio.readline()

#             time.sleep(DELAY)
        # except (KeyboardInterrupt, SystemExit, Exception): #when you press ctrl+c
           # print "\nKilling Thread..."
            # self.gpsp.running = False
            # self.gpsp.join() # wait for the thread to finish what it's doing
        # print("Done.\nExiting.")

    def log(self, message):
        self.out_q.put("log('" + str(message) + "')")

    def enter_ballast_state(self):
        # print("ballaststate packet", self.data_packet)
        # self.radio.write(self.data_packet)
        print("self.ballast_depth is: ", self.ballast_depth)
        reconnected_after_ballasting = False
        while not reconnected_after_ballasting:
            data = self.radio.readline()
            if data == DONE:
                print("data recieved is done, exiting ballasting")
                reconnected_after_ballasting = True
        return

    def manual_control(self, left, right, front, back):
        print('Set manual control: ', left, right, front, back)

    def ballast(self):
        print("Setting ballast")

    def close(self):
        sys.exit()


def main():
    """ Main method responsible for developing the main objects used during runtime
    like the BaseStation and Main objects. """

    # Parse arguments for debuging
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # Define Queue data structures in order to communicate between threads.
    to_GUI = Queue()
    to_BS = Queue()

    # Create a BS (base station) and GUI object thread.
    threaded_bs = BaseStation(args.debug, to_BS, to_GUI)
    threaded_bs.start()

    # Create main GUI object
    gui = Main(to_GUI, to_BS)


if __name__ == '__main__':
    main()
