'''
This class acts as the main functionality file for 
the Origin AUV. The "mind and brain" of the mission.
'''
# System imports
import os
import sys
import threading

# Custom imports
from api import Radio
from api import IMU
from api import PressureSensor


class AUV(threading.Thread):
    def __init__(self):
        # Call super class constructor (inheritance)
        threading.Thread.__init__(self)

        self.radio = None
        try:
            self.radio = Radio()


# Main function that is run upon execution of auv.py
def main():
    auv = AUV()


if __name__ == '__main__':  # If we are executing this file as main
    main()
