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
KNOTS_TO_METERSPERSEC = 1852/3600
DEBUG = False


class MotorQueue(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        self.mc = MotorController()
        self.imu = IMU.BNO055(serial_port='/dev/serial0', rst=18)
        self.gps = None
        threading.Thread.__init__(self)

        # DEAD RECKONING VARIABLES
        # Acceleration vector
        self.aX, self.aY, self.aZ = 0, 0, 0
        # Velocity vector
        self.vX, self.vY, self.vZ = 0, 0, 0
        # Position vector
        self.pX, self.pY, self.pZ = 0, 0, 0
        # Number of consecutive function calls with no acceleration
        self.noAccCount = 0
        # Time of last function call
        self.timeDeadReckoning = 0

    def reset_position(self):
        self.pX, self.pY, self.pZ = 0, 0, 0

    def dead_reckoning(self):
        # Initialize acceleration vector to be calculated later
        aX, aY, aZ = 0, 0, 0
        # Initialize velocity vector to be calculated later
        vX, vY, vZ = 0, 0, 0
        # Initialize position vector to be calculated later
        pX, pY, pZ = 0, 0, 0

        # minAccelTolerance: Any acceleration within 0.5 m/s^2 is set to 0 to reduce noise
        minAccelTolerance = 0.5
        # sampleCount: Takes average acceleration over 10 samples
        sampleCount = 10
        # noMovement: Total times needed to reset velocity to 0 to reduce noise
        noMovement = 5
        # timeNowDeadReckoning: Current time this function is called (in nanoseconds)
        timeNowDeadReckoning = time.time_ns()
        # interval: time difference between function calls (in seconds)
        interval = (timeNowDeadReckoning - self.timeDeadReckoning) * 1e-9

        # Calculate acceleration vector as an average over 10 samples
        for i in range(sampleCount):
            linAcc = self.imu.read_linear_acceleration()
            aX += linAcc[0]
            aY += linAcc[1]
            aZ += linAcc[2]

        aX /= sampleCount
        aY /= sampleCount
        aZ /= sampleCount

        # Set acceleration to 0 if in window to reduce noise
        if aX > -minAccelTolerance and aX < minAccelTolerance:
            aX = 0
        elif aY > -minAccelTolerance and aY < minAccelTolerance:
            aY = 0
        elif aZ > -minAccelTolerance and aZ < minAccelTolerance:
            aZ = 0

        # Keep running count of consecutive times with no acceleration in all axes
        if aX == 0 and aY == 0 and aZ == 0:
            self.noAccCount += 1
        else:
            self.noAccCount = 0

        # Zero out velocity if consecutive times with no acceleration to reduce noise
        if self.noAccCount > noMovement:
            self.vX, self.vY, self.vZ = 0, 0, 0
            self.noAccCount = 0

        # Integrate acceleration to find velocity
        vX = self.vX + (self.aX + (aX - self.aX) / 2.0) * interval
        vY = self.vY + (self.aY + (aY - self.aY) / 2.0) * interval
        vZ = self.vZ + (self.aZ + (aZ - self.aZ) / 2.0) * interval

        # Integrate velocity to find position
        pX = self.pX + (self.vX + (vX - self.vX) / 2.0) * interval
        pY = self.pY + (self.vY + (vY - self.vY) / 2.0) * interval
        pZ = self.pZ + (self.vZ + (vZ - self.vZ) / 2.0) * interval

        print("Current position in meters (relative): {}, {}, {}".format(pX, pY, pZ))

        # Update instance variables for next function call
        self.aX, self.aY, self.aZ = aX, aY, aZ
        self.vX, self.vY, self.vZ = vX, vY, vZ
        self.pX, self.pY, self.pZ = pX, pY, pZ

        self.timeDeadReckoning = timeNowDeadReckoning

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
        """
        Turns the auv y degrees then moves x meters.
        """
        # stops auv
        self.mc.zero_out_motors()

        if self.imu is not None:
            try:
                heading, _, _ = self.imu.read_euler()
                #print('HEADING=', heading)
            except:
                heading = 0
                print("IMU not found in run_motors in MotorQueue")
                return

        # modulo: a mod function that retains negatives (ex. -1 % 360 = -1)
        def modulo(x, y): return x % y if x > 0 else -1 * (abs(x) % y)

        # turn_error: Calculates distance between target and heading angles
        # modulo(target - heading, 360) -> absolute distance between both angles
        # needed because imu only contains 0-360 degrees, need to account for
        # negative angles and angles > 360
        def turn_error(target, heading): return modulo(target - heading, 360)

        # Turning with PID, might need to tune PID values
        target = heading + y    # Target angle to turn to
        turn_pid = PID(self.mc, 0, TURN_CONTROL_TOLERANCE, TURN_TARGET_TOLERANCE, DEBUG)
        heading, _, _ = self.imu.read_euler()

        turn_speed = turn_pid.pid(turn_error(target, heading))

        while turn_speed != 0:
            self.mc.update_motor_speeds([0, turn_speed, 0, 0])
            heading, _, _ = self.imu.read_euler()
            turn_speed = turn_pid.pid(turn_error(target, heading))
            print("turn speed: {0}, distance from target (degrees): {1}, heading: {2}".format(turn_speed, turn_error(target, heading), heading))
            time.sleep(LOOP_SLEEP_DELAY)

        self.mc.zero_out_motors()

        # Turning is complete, now move to place
        # Move to place using PID
        forward_pos = 0
        forward_pid = PID(self.mc, x, FORWARD_CONTROL_TOLERANCE, FORWARD_TARGET_TOLERANCE, DEBUG)
        turn_speed = turn_pid.pid(turn_error(target, heading))
        forward_speed = forward_pid.pid(forward_pos)
        self.reset_position()

        while forward_speed != 0:
            # Reorient turning if imu says it is off from target
            heading, _, _ = self.imu.read_euler()
            turn_speed = turn_pid.pid(turn_error(target, heading))

            # Figure out speed to use to move forward
            self.dead_reckoning()
            forward_pos = self.pX
            forward_speed = forward_pid.pid(forward_pos)
            #forward_pos += gps.speed * KNOTS_TO_METERSPERSEC * LOOP_SLEEP_DELAY
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
