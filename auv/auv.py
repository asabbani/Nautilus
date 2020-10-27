'''
This class acts as the main functionality file for
the Nautilus AUV. The "mind and brain" of the mission.
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
from missions import *

# Constants for the AUV
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
IMU_PATH = '/dev/serial0'
PING = b'PING\n'
THREAD_SLEEP_DELAY = 0.05
CONNECTION_TIMEOUT = 3


def log(val):
    print("[AUV]\t" + val)


class AUV():
    """ Class for the AUV object. Acts as the main file for the AUV. """

    def __init__(self):
        """ Constructor for the AUV """
        self.radio = None
        self.pressure_sensor = None
        self.imu = None
        self.mc = MotorController()
        self.connected_to_bs = False
        self.time_since_last_ping = 0.0
        self.current_mission = None

        # Get all non-default callable methods in this class
        self.methods = [m for m in dir(AUV) if not m.startswith('__')]

        try:
            self.pressure_sensor = PressureSensor()
            log("Pressure sensor has been found")
        except:
            log("Pressure sensor is not connected to the AUV.")

        try:
            self.imu = IMU(IMU_PATH)
            log("IMU has been found.")
        except:
            log("IMU is not connected to the AUV on IMU_PATH.")

        try:
            self.radio = Radio(RADIO_PATH)
            log("Radio device has been found.")
        except:
            log("Radio device is not connected to AUV on RADIO_PATH.")

        self.main_loop()

    def xbox(self, data):
        self.mc.update_motor_speeds(data)

    def test_motor(self, motor):
        """ Method to test all 4 motors on the AUV """

        if motor == "FORWARD":  # Used to be LEFT motor
            self.mc.test_forward()
        elif motor == "TURN":  # Used to be RIGHT MOTOR
            self.mc.test_turn()
        elif motor == "FRONT":
            self.mc.test_front()
        elif motor == "BACK":
            self.mc.test_back()
        elif motor == "ALL":
            self.mc.test_all()
        else:
            raise Exception('No implementation for motor name: ', motor)

    def main_loop(self):
        """ Main connection loop for the AUV. """

        log("Starting main connection loop.")
        while True:

            # Always try to update connection status.
            if time.time() - self.time_since_last_ping > CONNECTION_TIMEOUT:
                # Line read was EMPTY, but 'before' connection status was successful? Connection verification failed.
                if self.connected_to_bs is True:
                    log("Lost connection to BS.")

                    # reset motor speed to 0 immediately
                    self.mc.update_motor_speeds([0, 0, 0, 0])
                    log("DEBUG TODO speeds reset")

                    self.connected_to_bs = False

            if self.radio is None or self.radio.is_open() is False:
                try:  # Try to connect to our devices.
                    self.radio = Radio(RADIO_PATH)
                    log("Radio device has been found!")
                except:
                    pass
            else:
                try:
                    # Always send a connection verification packet and attempt to read one.
                    # self.radio.write(AUV_PING)
                    self.radio.write(PING)

                    if self.connected_to_bs is True:  # Send our AUV packet as well.

                        # TODO Data sending logic
                        #
                        # if (sending_data):
                        #    if(data.read(500000) != EOF)
                        #        send("d("+data.nextBytes+")")
                        #    else:
                        #        send("d_done()")
                        #        sending_data = False

                        if self.imu is not None:
                            try:
                                heading = self.imu.quaternion[0]
                                if heading is not None:
                                    heading = round(
                                        abs(heading * 360) * 100.0) / 100.0

                                    temperature = self.imu.temperature
                                    # (Heading, Temperature)
                                    if temperature is not None:
                                        self.radio.write(str.encode(
                                            "auv_data(" + str(heading) + ", " + str(temperature) + ")\n"))
                            except:
                                pass

                    # Read ALL lines stored in buffer (probably around 2-3 commands)
                    lines = self.radio.readlines()
                    self.radio.flush()

                    for line in lines:
                        if line == PING:  # We have a ping!
                            self.time_since_last_ping = time.time()
                            if self.connected_to_bs is False:
                                log("Connection to BS verified.")
                                self.connected_to_bs = True

                                # TODO test case: set motor speeds
                                data = [1, 2, 3, 4]
                                self.xbox(data)

                        elif len(line) > 1:
                            # Line was read, but it was not equal to a BS_PING
                            log(
                                "Possible command found. Line read was: " + str(line))

                            # Decode into a normal utd-8 encoded string and delete newline character
                            message = line.decode('utf-8').replace("\n", "")

                            if len(message) > 2 and "(" in message and ")" in message:
                                # Get possible function name
                                possible_func_name = message[0:message.find(
                                    "(")]

                                if possible_func_name in self.methods:
                                    log(
                                        "Recieved command from base station: " + message)
                                    self.time_since_last_ping = time.time()
                                    self.connected_to_bs = True

                                    try:  # Attempt to evaluate command.
                                        # Append "self." to all commands.
                                        eval('self.' + message)
                                        self.radio.write(str.encode(
                                            "log(\"[AUV]\tSuccessfully evaluated command: " + possible_func_name + "()\")\n"))
                                    except Exception as e:
                                        # log error message
                                        log(str(e))
                                        # Send verification of command back to base station.
                                        self.radio.write(str.encode("log(\"[AUV]\tEvaluation of command " +
                                                                    possible_func_name + "() failed.\")\n"))

                except Exception as e:
                    log("Error: " + str(e))
                    self.radio.close()
                    self.radio = None
                    log("Radio is disconnected from pi!")
                    continue

            if(self.current_mission is not None):
                self.current_mission.loop()

            time.sleep(THREAD_SLEEP_DELAY)

    def start_mission(self, mission):
        """ Method that uses the mission selected and begin that mission """
        if(mission == 0):  # Echo-location.
            try:  # Try to start mission
                self.current_mission = Mission1(
                    self, self.mc, self.pressure_sensor, self.imu)
                log("Successfully started mission " + str(mission) + ".")
                self.radio.write(str.encode("mission_started("+str(mission)+")\n"))
            except:
                raise Exception("Mission " + str(mission) +
                                " failed to start. Error: " + str(e))
        # elif(mission == 2):
        #     self.current_mission = Mission2()
        # if self.current_mission is None:
        #     self.current_mission = Mission1()

    def d_data(self):
        # TODO Set sending data flag
        # self.sending_data = true
        pass

    def abort_mission(self):
        aborted_mission = self.current_mission
        self.current_mission = None
        aborted_mission.abort_loop()
        log("Successfully aborted the current mission.")
        self.radio.write(str.encode("mission_failed()\n"))


def main():
    """ Main function that is run upon execution of auv.py """
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
