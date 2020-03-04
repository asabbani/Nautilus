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
PING = b'PING\n'
THREAD_SLEEP_DELAY = 0.3
CONNECTION_WAIT_TIME = 0.5


class AUV():
    """ Class for the AUV object. Acts as the main file for the AUV. """

    def __init__(self):
        """ Constructor for the AUV """

        self.radio = None
        self.mc = MotorController()
        self.connected_to_bs = False

        self.current_mission = ""

        # Get all non-default callable methods in this class
        self.methods = [m for m in dir(AUV) if not m.startswith('__')]

        try:
            self.radio = Radio(RADIO_PATH)
            print("Radio device has been found")
        except:
            print("Radio device is not connected to AUV on RADIO_PATH")

        self.main_loop()

    def test_motor(self, motor):
        if motor == "LEFT":
            self.mc.test_left()
        elif motor == "RIGHT":
            self.mc.test_right()
        elif motor == "FRONT":
            self.mc.test_front()
        elif motor == "BACK":
            self.mc.test_back()
        elif motor == "ALL":
            self.mc.test_all()

    def main_loop(self):
        """ Main connection loop for the AUV. """

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
                    # Always send a connection verification packet and attempt to read one.
                    # self.radio.write(AUV_PING)
                    self.radio.write(PING)
                    line = self.radio.readline()
                except:
                    self.radio.close()
                    self.radio = None
                    print("Radio is disconnected from pi!")
                    continue

                # Save previous connection status
                self.before = self.connected_to_bs

                # Updated connection status
                self.connected_to_bs = (line == PING)

                if self.connected_to_bs:
                    # If there was a status change, print out updated
                    if self.before is False:
                        # TODO
                        print("Connection to BS verified. Returning ping.")

                elif len(line) > 0:
                    # Line was read, but it was not equal to a BS_PING
                    print("Possible command found. Line read was: " + str(line))

                    # Attempt to split line into a string array after decoding it to UTF-8.
                    # EX: line  = "command arg1 arg2 arg3..."
                    #     cmd_array = [ "command", "arg1", "arg2" ]
                    cmd_array = line.decode(
                        'utf-8').replace("\n", "").split(" ")

                    if len(cmd_array) > 0 and cmd_array[0] in self.methods:
                        dummy = True
                        # build the 'cmd' string (using the string array) to: "self.command(arg1, arg2)"
                        cmd = "self." + cmd_array[0] + "("
                        for i in range(1, len(cmd_array)):
                            cmd += cmd_array[i]
                            if "\'" in cmd_array[i]:
                                dummy = not dummy
                            if dummy is True:
                                cmd += ","
                            else:
                                cmd += " "
                        cmd += ")"

                        print("Evaluating command: ", cmd)

                        try:
                            print("THIS WORKED")  # TODO
                            # Attempt to evaluate command. => Uses Vertical Pole '|' as delimiter
                            eval(cmd)
                            self.radio.write(str.encode(
                                "log \"Successfully evaluated task: " + cmd + "\"\n"))
                        except:
                            # Send verification of command back to base station.
                            self.radio.write(str.encode(
                                "log \"Failed to evaluate task: " + cmd + "\"\n"))

                elif self.before:
                    # Line read was EMPTY, but 'before' connection status was successful? Connection verification failed.
                    print("Connection verification to BS failed.")

            time.sleep(THREAD_SLEEP_DELAY)

    def start_mission(self, mission):
        print(mission)  # test stuff
        self.current_mission = mission


def main():
    """ Main function that is run upon execution of auv.py """
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
