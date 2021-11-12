import threading
import time

from queue import Queue
from . import MotorController

LOOP_SLEEP_DELAY = 0.005


class MotorQueue(threading.Thread):

    def __init__(self, queue):
        self.queue = queue
        self.mc = MotorController()
        threading.Thread.__init__(self)

    def run(self):

        while True:
            if not self.queue.empty():
                x, y, z = self.queue.get()
                if z == 0:
                    self.run_motors(x, y)
                if z == 1:
                    self.xbox_commands(x, y)
                elif z==2:
                    self.test_foward()
                elif z==3:
                    self.test_backward()
                elif z==4:
                    self.test_left()
                elif z==5:
                    self.test_right()
                elif z==6:
                    self.test_down()

            time.sleep(LOOP_SLEEP_DELAY)

    # for tests only
    def run_motors(self, x, y):
        # stops auv
        self.mc.zero_out_motors()

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

    def xbox_commands(self, x, y):
        x = round(x/100 * 150, 1)
        y = round(y/100 * 150, 1)
        self.mc.update_motor_speeds([y, x, 0, 0])
    
    #TODO implement actual tests
    # def test_forward(self):
    # def test_backward(self):
    # def test_left(self):
    #     turn_speed = -90
    # def test_right(self):
    #     turn_speed = 90
    # def test_down(self):

