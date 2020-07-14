"""
The radio class enables communication over wireless serial radios.
"""
import serial

TIMEOUT_DURATION = 2
DEFAULT_BAUDRATE = 115200


class Radio():
    def __init__(self, serial_path, baudrate=DEFAULT_BAUDRATE):
        """
        Initializes the radio object.

        serial_path: Absolute path to serial port for specified device.
        """

        # Establish connection to the serial radio.
        self.ser = serial.Serial(serial_path,
                                 baudrate=baudrate, parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                                 timeout=TIMEOUT_DURATION
                                 )

    def write(self, message):
        """
        Sends provided message over serial connection.

        message: A string message that is sent over serial connection.
        """
        self.ser.write(message)

    def readlines(self):
        """
        Returns an array of lines
        """
        return self.ser.readlines()

    def readline(self):
        """
        Returns a string from the serial connection.
        """
        return self.ser.readline()

    def is_open(self):
        """
        Returns a boolean if the serial connection is open.
        """
        return self.ser.is_open

    def flush(self):
        """
        Clears the buffer of the serial connection.
        """
        self.ser.flush()

    def close(self):
        """
        Closes the serial connection
        """
        self.ser.close()
