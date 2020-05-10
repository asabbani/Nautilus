from api import motor_controller
import threading


class Mission1(threading.Thread):
    def __init__(self, motor_controller, pressure_sensor, IMU, in_q, out_q):
        """ TODO Function Header """

        # superclass
        threading.Thread.__init__(self)

        self.motor_controller = motor_controller
        self.pressure_sensor = pressure_sensor
        self.IMU = IMU
        self.in_q = in_q
        self.out_q = out_q

    def check_tasks(self):
        while(self.in_q.empty() is False):
            task = self.in_q.get()
            print("Found task: " + task)

            # Try to evaluate the task in the in_q.
            try:
                eval("self." + task)
            except:
                print("Could not evaluate task: ", task)

    def loop(self):

    def find_source(self):

    def move_to_source(self):
        """ TODO FUNCTION HEADER """
        # only move to source if the auv is in position to move
        motor_speed_array = [10, 10, 0, 0]  # sync the left and right motors
        self.motor_controller.update_motor_speeds(motor_speed_array)
