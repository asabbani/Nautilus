import signal
import time
from xbox360controller import Xbox360Controller

class Xbox(Xbox360Controller):

    def __init__(self):
        print("attempting superclass")
        super().__init__(0, axis_threshold=0.2)
        print("superclass did something")

    def leftX(self):
        return self.button_thumb_l._value #TODO

    def rightTrigger(self):
        return self.trigger_r.value

    def leftTrigger(self):
        return self.trigger_l.value


