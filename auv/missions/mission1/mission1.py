import threading


class Mission1(threading.Thread):
    def __init__(self, motor_controller, pressure_sensor, IMU):
        """ TODO Function Header """

        self.motor_controller = motor_controller
        self.pressure_sensor = pressure_sensor
        self.IMU = IMU

    def loop(self):
        pass

    def find_source(self):
        pass

    def move_to_source(self):
        """ TODO FUNCTION HEADER """
        # only move to source if the auv is in position to move
        motor_speed_array = [10, 10, 0, 0]  # sync the left and right motors
        self.motor_controller.update_motor_speeds(motor_speed_array)
