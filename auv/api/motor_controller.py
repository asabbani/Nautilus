"""
The motor_controller class calibrates and sets the speed of all of the motors
"""

# System imports
import time

# Custom Imports
import pigpio
import RPi.GPIO as io
from api import Motor
from api import IMU
from api import PressureSensor
import math


IMU_PATH = '/dev/serial0'


# # GPIO Pin numbers for Motors
# FORWARD_GPIO_PIN = 4  # 18
# TURN_GPIO_PIN = 11  # 24
# FRONT_GPIO_PIN = 18  # 4
# BACK_GPIO_PIN = 24  # 11


# # Define pin numbers for PI (Not the same as GPIO?)
# FORWARD_PI_PIN = 7          # Left pins
# TURN_PI_PIN = 23            # Right pins
# FRONT_PI_PIN = 12           # Back pins
# BACK_PI_PIN = 18            # Front pins

FORWARD_GPIO_PIN = 0         # in the back
BACKWARD_GPIO_PIN = 1        # in the front
LEFT_GPIO_PIN = 2           # goes up/down
RIGHT_GPIO_PIN = 3           # goes up/down
DOWN_GPIO_PIN = 4           # goes up/down


FORWARD_PI_PIN = 0         # in the back
BACKWARD_PI_PIN = 1            # in the front
LEFT_PI_PIN = 2           # goes up/down
RIGHT_PI_PIN = 3           # goes up/down
DOWN_PI_PIN = 4            # goes up/down

# Indices for motor array
FORWARD_MOTOR_INDEX = 0         # in the back
BACKWARD_MOTOR_INDEX = 1            # in the front
LEFT_MOTOR_INDEX = 2           # goes up/down
RIGHT_MOTOR_INDEX = 3           # goes up/down
DOWN_MOTOR_INDEX = 4            # goes up/down

# Constants
BALLAST = 4
MAX_PITCH = 30
MAX_CORRECTION_MOTOR_SPEED = 25  # Max turning speed during pid correction


def log(val):
    """ Adapt log to note the object we are in """
    print("[MC]\t" + val)


class MotorController:
    """
    Object that contains all interactions with the motor array for the AUV
    """

    def __init__(self, queue):
        """
        Initializes MotorController object and individual motor objects
        to respective gpio pins.
        """

        self.pressure_sensor = PressureSensor()
        self.pressure_sensor.init()

        self.imu = IMU.BNO055(serial_port='/dev/serial0', rst=18)
        # Connection to Raspberry Pi GPIO ports.
        self.pi = pigpio.pi()

        # Motor object definitions.
        self.motor_pins = [FORWARD_GPIO_PIN, BACKWARD_GPIO_PIN,
                           LEFT_GPIO_PIN, RIGHT_GPIO_PIN, DOWN_GPIO_PIN]

        self.pi_pins = [FORWARD_PI_PIN, BACKWARD_PI_PIN, LEFT_PI_PIN, RIGHT_PI_PIN, DOWN_PI_PIN]

        self.motors = [Motor(gpio_pin=pin, pi=self.pi)
                       for pin in self.motor_pins]

        self.forward_speed = 0
        self.back_speed = 0
        self.left_speed = 0
        self.right_speed = 0
        self.down_speed = 0
        self.motor_queue = queue
#        self.check_gpio_pins()

    def update_motor_speeds(self, data):
        """
        Sets motor speeds to each individual motor. This is for manual (xbox) control when the
        radio sends a data packet of size 4.

        data: String read from the serial connection containing motor speed values.
        """
        if len(data) != len(self.motors):
            raise Exception(
                "Data packet length does not equal motor array length.")
            return

        # Parse motor speed from data object.

        self.forward_speed = data[FORWARD_MOTOR_INDEX]
        self.backward_speed = data[BACKWARD_MOTOR_INDEX]
        self.left_speed = data[LEFT_MOTOR_INDEX]
        self.right_speed = data[RIGHT_MOTOR_INDEX]
        self.down_speed = data[DOWN_MOTOR_INDEX]


        log("motors is: " + str(data))

        # Set motor speed
        self.motors[FORWARD_MOTOR_INDEX].set_speed(self.forward_speed)
        self.motors[BACKWARD_MOTOR_INDEX].set_speed(self.backward_speed)
        self.motors[LEFT_MOTOR_INDEX].set_speed(self.left_speed)
        self.motors[RIGHT_MOTOR_INDEX].set_speed(self.right_speed)
        self.motors[DOWN_MOTOR_INDEX].set_speed(self.down_speed)

    def pid_motor(self, pid_feedback):
        """
        Updates the TURN motor based on the PID feedback. 

        feedback: Feedback value from pid class.
        """
        if(not pid_feedback):
            self.turn_speed = 0
        else:
            self.turn_speed = self.calculate_pid_new_speed(pid_feedback)

#        log('[PID_MOTOR] %7.2f %7.2f' %
 #             (self.left_speed, self.right_speed), end='\n')

        self.motors[TURN_MOTOR_INDEX].set_speed(self.turn_speed)

    def pid_motor_pitch(self, pid_feedback, current_value):
        """
        Updates front and back  motor speed based off pid feedback

        feedback: Feedback value from pid class.
        """
        if(not pid_feedback):
            self.front_speed = 0
            self.backward_speed = 0
        elif abs(current_value) > 30:
            # double the motor speed for the motor in the water
            double_motor_speed = pid_feedback * 2
            if current_value > MAX_PITCH:
                # Front motor is out of water, set speed to 0 to prevent breaking
               # When not flipped: vvvv
                self.front_speed = 0
                self.backward_speed = self.calculate_pid_new_speed(
                    -double_motor_speed)
               # WHen flipped: vvvv
               # self.front_speed = self.calculate_pid_new_speed(double_motor_speed)
               # self.back_speed = 0
            else:
                # Back motor is out of water, set speed to 0 for front motor
                # WHen not flipped: vvvv
                self.front_speed = self.calculate_pid_new_speed(
                    double_motor_speed)
                self.backward_speed = 0
                # WHen flipped: vvv
                #self.front_speed = 0
                #self.back_speed = self.calculate_pid_new_speed(-double_motor_speed)
        else:

            # When not flipped, use +
            self.front_speed = self.calculate_pid_new_speed(+pid_feedback)
            # When not flipped, use -
            self.backward_speed = self.calculate_pid_new_speed(-pid_feedback)

      #  log('[PID_MOTOR] %7.2f %7.2f' %
     #         (self.front_speed, self.back_speed), end='\n')
        self.motors[FRONT_MOTOR_INDEX].set_speed(self.front_speed)
        self.motors[BACK_MOTOR_INDEX].set_speed(self.backward_speed)

    def zero_out_motors(self):
        """
        Sets motor speeds of each individual motor to 0.
        """
        for motor in self.motors:
            motor.set_speed(0)

        log("motors set to [0, 0, 0, 0]")


    def test_all(self):
        """
        Calibrates each individual motor.
        """
        log('Testing all motors...')
        for motor in self.motors:
            motor.test_motor()
            time.sleep(1)

    def test_forward(self):  # Used to be left motor
        log('Testing forward motor...')
        #self.motors[FORWARD_MOTOR_INDEX].test_motor()
        self.motor_queue.put((0,0,2))

    def test_backward(self):  # used to be right motor
        log('Testing turn motor...')
        #self.motors[BACKWARD_MOTOR_INDEX].test_motor()
        self.motor_queue.put((0,0,3))

    def test_left(self):
        # heading = 359
        log('Testing front motor...')
        self.motor_queue.put((0,0,4))
        # while heading >= 270:
        #     self.motors[LEFT_MOTOR_INDEX].test_motor()
        #     heading, _, _ = self.imu.read_euler()

    def test_right(self):
        # heading = 0
        log('Testing back motor...')
        self.motor_queue.put((0,0,5))
        # while heading <= 90:
        #     self.motors[RIGHT_MOTOR_INDEX].test_motor()
        #     heading, _, _ = self.imu.read_euler()
    

    def test_down(self):        
        log('Testing back motor...')
        self.motor_queue.put((0,0,6))
        # if self.pressure_sensor is not None:
        #     startDepth = (self.pressure_sensor-1013.25)/1000 * 10.2
        #     currentDepth = startDepth
        #     while math.abs(currentDepth - startDepth) <= 5:
        #         self.pressure_sensor.read()
        #         currentDepth = (self.pressure_sensor-1013.25)/1000 * 10.2
        #         self.motors[DOWN_MOTOR_INDEX].test_motor()

    def check_gpio_pins(self):
        """ This function might be deprecated... """
        io.setmode(io.BOARD)
        for pins in self.pi_pins:
            io.setup(pins, io.IN)
            print("Pin: ", pins, io.input(pins))
            #log("Pin:", pins, io.input(pins))

    def calculate_pid_new_speed(self, feedback):
        # Case 1: Going backward
        if (feedback < 0):
            return min(100 + abs(feedback), 100 + MAX_CORRECTION_MOTOR_SPEED)
        # Case 2: Going forward
        else:
            return min(feedback, MAX_CORRECTION_MOTOR_SPEED)


def main():
    mc = MotorController()
    mc.test_all()


if __name__ == '__main__':
    main()
    # def calculate_pid_new_speed(self, last_speed, speed_change):
    #     #log(">>Last speed\t" + str(last_speed) + "speed_change\t" + str(speed_change))
    #     #new_speed = last_speed + speed_change
    #     # Case 1: was going forward
    #     assert(not (MAX_CORRECTION_MOTOR_SPEED < last_speed and last_speed <= 100)), "Unexpected last speed" + str(last_speed)
    #     assert(not (100 + MAX_CORRECTION_MOTOR_SPEED < last_speed and last_speed <= 200)), "Unexpected last speed" + str(last_speed)
    #     if(last_speed <= MAX_CORRECTION_MOTOR_SPEED):
    #         new_speed = last_speed + speed_change
    #         lower_speed_cap = 0
    #         upper_speed_cap = MAX_CORRECTION_MOTOR_SPEED
    #     # Case 2: was going backward
    #     else:
    #         new_speed = last_speed - speed_change
    #         lower_speed_cap = 100
    #         upper_speed_cap = 100 + MAX_CORRECTION_MOTOR_SPEED
    #
    #
    #     # Exceed speed range, too big
    #     if(new_speed > upper_speed_cap):
    #         new_speed = upper_speed_cap
    #     # Exceed, too small
    #     if(new_speed < lower_speed_cap):
    #
    #         # Was going forward, want to backward
    #         if(last_speed <= MAX_CORRECTION_MOTOR_SPEED):
    #             #log("Adjust case forward -> backward")
    #             new_speed = abs(new_speed) + 100
    #             # if it goes backward too fast
    #             if(new_speed > 100 + MAX_CORRECTION_MOTOR_SPEED):
    #                 new_speed = 100 + MAX_CORRECTION_MOTOR_SPEED
    #         else: # was going backward, want to forward
    #             #log("Adjust case backward -> forward")
    #             new_speed = 100 - new_speed
    #             # if it goes forward too fast
    #             if(new_speed > MAX_CORRECTION_MOTOR_SPEED):
    #                 new_speed = MAX_CORRECTION_MOTOR_SPEED
    #
    #     assert(not (MAX_CORRECTION_MOTOR_SPEED < new_speed and new_speed <= 100)), "Unexpected new speed output" + str(new_speed)
    #     assert(not (100 + MAX_CORRECTION_MOTOR_SPEED < new_speed and new_speed <= 200)), "Unexpected new speed output" + str(new_speed)
    #     return new_speed
