import threading

# Constants for the base station
THREAD_SLEEP_DELAY = 0.1  # Since we are the slave to AUV, we must run faster.
PING_SLEEP_DELAY = 3
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'

PING = 0xFFFFFF

CONNECTION_TIMEOUT = 6

# AUV Constants (these are also in auv.py)
MAX_AUV_SPEED = 100
MAX_TURN_SPEED = 50

# determines if connected to BS
connected = False
lock = threading.Lock()
radio_lock = threading.Lock()
