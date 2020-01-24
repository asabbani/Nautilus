# TODO, someone needs to fix this. 

import threading
from gps3 import gps3  # https://pypi.org/project/gps3/

# Class for basic GPS functionality
class GPS(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) # Threading studd

        self.gps_socket  = None
        self.data_stream = None
        self.running     = False
        self.speed       = 0
        self.latitude    = 0
        self.longitude   = 0
        self.altitude    = 0

        # Try to connect to GPSD socket
        try:
      #      self.gps_socket = gps3.GPSDSocket()    # => There is an Error here... IDK how to fix
      #      self.data_stream = gps3.DataStream()
            pass
        except:
            print ("Cannot access GPSD service.")

        if (self.gps_socket != None):
            self.gps_socket.connect()
            self.gps_socket.watch()

    # Start running GPS data
    def startGPS():
        self.running = True

    # Runs continuously on new thread
    def run(self):
        if self.running:
            for new_data in self.gps_socket: # Wait for new data on gps socket
                if new_data:
                    self.data_stream.unpack(new_data)

            #         code below has an error, apparently there is no TPV member in data_stream
               #     self.speed = self.data_stream.TPV['speed']
               #     self.latitude = self.data_stream.TPV['lat']
               #     self.longitude = self.data_stream.TPV['lon']
               #     self.altitude = self.data_stream.TPV['alt']
