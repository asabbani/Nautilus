# Custom imports
import serial
from adafruit_bno055 import BNO055_UART as super_imu
import time


class IMU(super_imu):
    """ Utilize inheritance of the low-level parent class """

    def __init__(self, path):
        """ Simply call our superclass constructor """
        super().__init__(serial.Serial(path))
