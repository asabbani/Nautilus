# TODO, someone needs to fix this.

import threading
import time
import sys
from gps3 import gps3  # https://pypi.org/project/gps3/


class GPS(threading.Thread):
    """ Class for basic GPS functionality """

    def __init__(self, out_queue):
        # Call the threading super-class constructor (inheritance)
        threading.Thread.__init__(self)

        self.gps_socket = None
        self.data_stream = None
        self.running = False
        self.out_q = out_queue

        # Try to connect to GPSD socket (if gpsd is not installed, this will error)
        try:
            # TODO something happens here on OSX i guess?
            self.gps_socket = gps3.GPSDSocket()
            self.data_stream = gps3.DataStream()
        except:
            raise Exception(
                "[GPS] Could not create gpsd-socket or data stream object.")

        # Start our thread
        self.start()

    def run(self):

        while (True):
            if (self.gps_socket is not None):
                self.gps_socket.connect()
                self.gps_socket.watch()

                for new_data in self.gps_socket:  # Wait for new data on gps socket
                    if new_data:
                        self.data_stream.unpack(new_data)

                        # Send gps data (as a dictionary/hashmap) to the synchronous Queue data structure
                        self.out_q.push({
                            speed: self.data_stream.TPV['speed'],
                            latitude: self.data_stream.TPV['lat'],
                            longitude: self.data_stream.TPV['lon'],
                            altitude: self.data_stream.TPV['alt']
                        })

            # Sleep for 4 seconds
            time.sleep(4)
