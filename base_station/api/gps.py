# TODO, someone needs to fix this.

import threading
from gps3 import gps3  # https://pypi.org/project/gps3/


class GPS(threading.Thread):
    """ Class for basic GPS functionality """

    def __init__(self):
        # Call the threading super-class constructor (inheritance)
        threading.Thread.__init__(self)

        self.gps_socket = None
        self.data_stream = None
        self.running = False
        self.speed = 0
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0

        # Try to connect to GPSD socket (if gpsd is not installed, this will error)
        try:
            # TODO something happens here on OSX i guess?
            self.gps_socket = gps3.GPSDSocket()
            self.data_stream = gps3.DataStream()
        except:
            pass  # TODO

        # TODO testing
        if (self.gps_socket is not None):
            self.gps_socket.connect()
            # self.gps_socket.watch()

    def start_GPS():
        """ Begins running the GPS"""
        self.running = True

    def run(self):
        if self.running:
            for new_data in self.gps_socket:  # Wait for new data on gps socket
                if new_data:
                    self.data_stream.unpack(new_data)

                    self.speed = self.data_stream.TPV['speed']
                    self.latitude = self.data_stream.TPV['lat']
                    self.longitude = self.data_stream.TPV['lon']
                    self.altitude = self.data_stream.TPV['alt']
