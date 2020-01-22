'''
This class manages the serial connection between the 
AUV and Base Station along with sending controller 
commands.
'''
import sys
import os

# Sets the PYTHONPATH to include the components.
#split_path = os.path.abspath(__file__).split('/')
#split_path = split_path[0:len(split_path) - 2]
sys.path.append('./api') # Include API folder
sys.path.append('./gui') # Include API folder

# System imports
import serial
import time
import math
import argparse

# Custom imports
from nav import xbox
from nav import NavController
from radio import Radio
from gps import *

SPEED_CALIBRATION = 10
IS_MANUAL = True
RADIO_PATH = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
NO_CALIBRATION = 9
CAL = 'CAL\n'
REC = 'REC\n'
DONE = "DONE\n"
DELAY = 0.08
#Hey we're using spaces
class BaseStation:
    def __init__(self, debug=False):

        '''
        Initialize Serial Port and Class Variables

        debug: debugging flag
        '''
    # Jack Silberman's radio
    # Yonder's radio
        #self.test_dict = {'A':10}
        self.radio = Radio(RADIO_PATH)
        self.data_packet = []       
        self.joy = None 	
        self.connected_to_auv = False
        self.navController = None
        self.debug = debug
        self.cal_flag = NO_CALIBRATION
        self.radio_timer = []
        self.gpsp = GpsPoller() # create the thread
        self.ballast_depth = 0
        self.button_cb = {'MAN':self.manual_control, 'BAL':self.ballast}

        
       # self.test = json.dumps(self.test_dict)

    def set_main(self, Main):
        self.main = Main 

    def calibrate_controller(self):
        '''
        Instantiates a new Xbox Controller Instance and NavigationController
        '''

        # Construct joystick and check that the driver/controller are working.
        self.joy = None
        self.main.log("Attempting to connect xbox controller")
        while self.joy is None:
            self.main.update()
            try:
                self.joy = xbox.Joystick()
            except Exception as e:
                continue
        self.main.log("Xbox controller is connected")                

        #Instantiate New NavController With Joystick
        self.navController = NavController(self.joy, self.button_cb, self.debug)
        
        self.main.log("Controller is connected")

    def calibrate_communication(self):
        '''
        Ensure communication between AUV and Base Station
        '''
        
        # Flush the serial connection.
        self.radio.flush()

        self.main.log("Attempting to establish connection to AUV...")
        self.main.update()

        # Wait until connection is established.
        while not self.connected_to_auv:
            # Send Calibration Signal To AUV
#            if self.radio.write(CAL) == -1:
 #               self.main.log("Radios have been physically disconnected. Check USB connection.")
              
            self.radio.write(CAL) 
            # Attempt to read from radio
            line = self.radio.readline()
            print("line read is: " , line) 
            # If we got an error (returned 0)
  #          if line == -1:
               # self.main.log("Radios have been physically disconnected. Check USB connection.")
   #         else:
            self.connected_to_auv = (line == CAL) or (line == REC)

            if not self.connected_to_auv:
                self.main.log("Connection timed out, trying again...")
                self.main.update()

        self.radio.flush()
        self.main.log("Connection established with AUV.")
        self.main.comms_status_string.set("Comms Status: Connected")
    def set_calibrate_flag(self, cal_flag):
        self.cal_flag = cal_flag

    def run(self):
        ''' 
        Runs the controller loop for the AUV.
        '''
         #try:
         #Start Control Loop
        self.radio.write(chr(SPEED_CALIBRATION))
       # self.gpsp.start()
        curr_time = time.time()

        #while self.connected_to_auv:
        while True:
            self.main.log("GPS: {}".format(self.gpsp.gpsd.fix.latitude)) 
            self.navController.handle()
#             #Get pa0cket
#             self.data_packet = self.navController.getPacket()
#             self.data_packet = self.data_packet + chr(self.cal_flag) + '\n'
#             print("Data packet: ", self.data_packet)
        
#             if IS_MANUAL:
#                 delta_time = time.time() - curr_time
#                 self.radio_timer.append( delta_time )
#                # print("writing json data of: " , json.dumps(self.test_dict) )
#                 self.radio.write(self.data_packet)
#                 #self.radio.write(json.dumps(self.test_dict) + '\n')
#                 curr_time = time.time()
            
#             #else:
#                 # Send packet for autonomous movement; Aborting mission, where is home, where is waypoint, start ballast, switch back to manual
#                 #auto_packet = [ isAborting, home_wp, wp_dest, ballast, is_Manual ]
            
#             #Reset motor calibration
#             self.cal_flag = NO_CALIBRATION  
#             if ord(self.data_packet[3]) == 1:
#                 self.main.log("Entering ballast state.")
#                 self.enter_ballast_state() 
#                 self.main.log("Finished ballasting.")
#                 self.radio.write(chr(SPEED_CALIBRATION))
            
#             # Await response from AUV.
#             if self.radio.readline() != 'REC\n':
            
#                 self.connected_to_auv = False
            
#                 print("WARNING - AUV disconnected. Attempting to reconnect.")
            
#                 self.calibrate_communication()
            
# #                data = self.radio.readline()
            
#             time.sleep(DELAY)
        self.main.update()
    
        #except (KeyboardInterrupt, SystemExit, Exception): #when you press ctrl+c
           # print "\nKilling Thread..."
            #self.gpsp.running = False
            #self.gpsp.join() # wait for the thread to finish what it's doing
        #print("Done.\nExiting.")
            

    def enter_ballast_state(self): 
        #print("ballaststate packet", self.data_packet)
        #self.radio.write(self.data_packet)
        print("self.ballast_depth is: ", self.ballast_depth)
        reconnected_after_ballasting = False
        while not reconnected_after_ballasting:
            data = self.radio.readline()
            if data == DONE:
                print("data recieved is done, exiting ballasting")
                reconnected_after_ballasting = True
        return
    def manual_control(self, left, right, front, back):
        print('Set manual control: ', left, right, front, back)
    def ballast(self):
        print("Setting ballast")
# TODO: Comment run, find out when auv disconnects.
def main(): 

    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    bs = BaseStation(debug=args.debug)
    

if __name__ == '__main__':
     main()
