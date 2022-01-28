'''
This class acts as the main functionality file for
the Nautilus AUV. The "mind and brain" of the mission.
'''
# System imports
import os
import sys
import threading
import time
import math

# Custom imports
from queue import Queue
from api import Radio
from api import IMU
from api import Crc32
from api import PressureSensor
from api import MotorController
from api import MotorQueue
from missions import *

from threads. import AUV_Send_Data, AUV_Receive, AUV_Send_Ping


def threads_active(ts):
    for t in ts:
        if t.is_alive():
            return True
    return False


if __name__ == '__main__':  # If we are executing this file as main
    queue = Queue()
    halt = [False]

    auv_motor_thread = MotorQueue(queue, halt)
    auv_r_thread = AUV_Receive(queue, halt)

    ts = []

    auv_s_thread = AUV_Send_Data()
    auv_ping_thread = AUV_Send_Ping()

    ts.append(auv_motor_thread)
    ts.append(auv_r_thread)
    ts.append(auv_s_thread)
    ts.append(auv_ping_thread)

    auv_motor_thread.start()
    auv_r_thread.start()
    auv_s_thread.start()
    auv_ping_thread.start()

    try:
        while threads_active(ts):
            time.sleep(1)
    except KeyboardInterrupt:
        # kill threads
        for t in ts:
            t.stop()

    print("waiting to stop")
    while threads_active(ts):
        time.sleep(0.1)
    print('done')
