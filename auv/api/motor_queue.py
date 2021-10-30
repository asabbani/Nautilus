import threading
import time

from queue import Queue
from . import MotorController
from . import IMU
from . import PID

LOOP_SLEEP_DELAY = 0.005

# PID Constants
TURN_CONTROL_TOLERANCE = 1       # Within 1 degree of target turn
TURN_TARGET_TOLERANCE = 1
FORWARD_CONTROL_TOLERANCE = 0.1  # Within 0.1 meters of target
FORWARD_TARGET_TOLERANCE = 0.1
DEBUG = True


class MotorQueue(threading.Thread):

    def __init__(self, queue):
        self.queue = queue
        self.mc = MotorController()
        self.imu = IMU.BNO055(serial_port='/dev/serial0', rst=18)
        threading.Thread.__init__(self)

    def run(self):

        while True:
            if not self.queue.empty():
                x, y, z = self.queue.get()
                if z == 0:
                    self.run_motors(x, y)
                if z == 1:
                    self.xbox_commands(x, y)

            time.sleep(LOOP_SLEEP_DELAY)

    # for tests only
    def run_motors(self, x, y):
        # stops auv
        self.mc.zero_out_motors()

        if self.imu is not None:
            try:
                heading, _, _ = self.imu.read_euler()
                #print('HEADING=', heading)
            except:
                # TODO print statement, something went wrong!
                heading = 0
                print("IMU not found in run_motors in MotorQueue")
                return

        # Turning with PID, might need to turn PID values
        target = heading + y    # Target angle to turn to
        turn_pid = PID(self.mc, target, TURN_CONTROL_TOLERANCE, TURN_TARGET_TOLERANCE, DEBUG)
        heading, _, _ = self.imu.read_euler()
        turn_speed = turn_pid.pid(heading)

        while turn_speed != 0:
            self.mc.update_motor_speeds([0, turn_speed, 0, 0])
            heading, _, _ = self.imu.read_euler()
            turn_speed = turn_pid.pid(heading)
            time.sleep(LOOP_SLEEP_DELAY)

        self.mc.zero_out_motors()

        # Turning is complete, now move to place
        # Move to place using PID
        forward_pos = 0
        forward_pid = PID(self.mc, x, FORWARD_CONTROL_TOLERANCE, FORWARD_TARGET_TOLERANCE, DEBUG)
        turn_speed = turn_pid.pid(heading)
        forward_speed = forward_pid.pid(forward_pos)

        while forward_speed != 0:
            # Reorient turning if imu says it is off from target
            heading, _, _ = self.imu.read_euler()
            turn_speed = turn_pid.pid(heading)

            # Figure out speed to use to move forward
            forward_speed = forward_pid.pid(forward_pos)
            forward_pos += forward_speed * LOOP_SLEEP_DELAY  # TODO Update forward_speed to use GPS speed once GPS is done

            self.mc.update_motor_speeds([forward_speed, turn_speed, 0, 0])
            time.sleep(LOOP_SLEEP_DELAY)

        """ OLD CODE
        forward_speed = 0
        turn_speed = 0

        # turn right
        if (y > 0):
            turn_speed = 90
        # turn left
        elif (y < 0):
            turn_speed = -90

        # turn auv
        self.mc.update_motor_speeds([0, turn_speed, 0, 0])

        # TODO implement so motors run until we've turned y degrees

        time.sleep(5)

        self.mc.zero_out_motors()

        # move forward
        if (x != 0):
            forward_speed = 90
            self.mc.update_motor_speeds([forward_speed, 0, 0, 0])

            # TODO implement so motors run until we've moved x meters
            time.sleep(5)

        self.mc.zero_out_motors()
        """

    def xbox_commands(self, x, y):
        x = round(x/100 * 150, 1)
        y = round(y/100 * 150, 1)
        self.mc.update_motor_speeds([y, x, 0, 0])
