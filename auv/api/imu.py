# Custom imports
import serial
from adafruit_bno055 import BNO055_UART as super_imu
import time


class IMU(super_imu):
    """ Utilize inheritance of the low-level parent class """

    def __init__(self, path):
        """ Simply call our superclass constructor """
        super().__init__(serial.Serial(path))

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
    # TODO Implement more useful functions other than the default

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
            linAcc = self.read_linear_acceleration()
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
