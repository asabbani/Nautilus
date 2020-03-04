from api import motor_controller
import threading


class Mission1(threading.Thread):
    def __init__(self, motor_controller):
        """ TODO Function Header """

        # superclass
        threading.Thread.__init__(self)

        self.motor_controller = motor_controller
