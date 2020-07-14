import time
import os
import RPi.GPIO as GPIO
import eeml
GPIO.setmode(GPIO.BCM)
DEBUG = 1
LOGGER = 1

GPIO.setup(0, GPIO.IN)
input = GPIO.input(0)

while True:
        pass

time.sleep(1)
