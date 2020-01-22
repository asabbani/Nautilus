# GPS Tester File

# Add parent directory to active path
import sys
sys.path.append('../')

# import necessary api to test GPS
from api import GPS
import time


my_gps = GPS()
my_gps.start()

# Begin testing
while(True):
    print("Altitude: ", my_gps.altitude)
    print("Latitude: ", my_gps.latitude)
    print("Longitude: ", my_gps.longitude)
    print("Speed: ", my_gps.speed)
    print("Sleeping....\n")
    time.sleep(2)




