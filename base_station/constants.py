# Constants for the base station
THREAD_SLEEP_DELAY = 0.1  # Since we are the slave to AUV, we must run faster.
PING_SLEEP_DELAY = 3
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'

PING = 0xFFFFFF

CONNECTION_TIMEOUT = 6

# AUV Constants (these are also in auv.py)
MAX_AUV_SPEED = 100
MAX_TURN_SPEED = 50


# Navigation Encoding
NAV_ENCODE = 0b000000100000000000000000           # | with XSY (forward, angle sign, angle)
XBOX_ENCODE = 0b111000000000000000000000          # | with XY (left/right, down/up xbox input)
MISSION_ENCODE = 0b000000000000000000000000       # | with X   (mission)
DIVE_ENCODE = 0b110000000000000000000000           # | with D   (depth)

# Action Encodings
HALT = 0b010
CAL_DEPTH = 0b011
ABORT = 0b100
DL_DATA = 0b101
