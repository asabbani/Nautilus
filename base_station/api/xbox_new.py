import signal
import time
from xbox360controller import Xbox360Controller

class Xbox(Xbox360Controller):

    def __init__(self):
        super.__init__(0, axis_threshold=0.2)

    def leftX(self):
        return 0 #TODO

    def rightTrigger(self):
        return self.trigger_r.value

    def leftTrigger(self):
        return self.trigger_l.value


