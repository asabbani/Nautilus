""" This class manages the GUI framework for the base_station
user-interface. """

# System imports
import sys
import os
import datetime

# Begin custom imports
from tkinter import *
from tkinter import Toplevel
from tkinter import messagebox
from tkinter.ttk import Combobox
from .map import Map

# Begin Constants
WIDTH = 1400
HEIGHT = 800
# Refresh time
REFRESH_TIME = 500
# Development resolution constants (used for proper screen scaling)
DEV_WIDTH = 1920.0
DEV_HEIGHT = 1080.0
# Frame heights
TOP_FRAME_HEIGHT = 550
BOT_FRAME_HEIGHT = 30
# Font Constants
FONT = "Courier New"
HEADING_SIZE = 20
BUTTON_SIZE = 14
STATUS_SIZE = 14
# Main frame paddings
MAIN_PAD_X = 5
MAIN_PAD_Y = 5
# Calibration panel paddings
CALIBRATE_PAD_Y = 10
# Combobox panel paddings
COMBO_PAD_X = 10
COMBO_PAD_Y = 3
# Button panel paddings
BUTTON_PAD_X = 10
BUTTON_PAD_Y = 3
# Button width and heigth (in text units)
BUTTON_WIDTH = 17
BUTTON_HEIGHT = 2
# Mission
MISSIONS = ["Sound Tracking", "Audio Collecting"]


class Main():
    """ Main GUI object that handles all aspects of the User-Interface """

    def __init__(self, in_q=None, out_q=None):
        # Begin initializing the main Tkinter (GUI) framework/root window
        self.root = Tk()

        # Code below is to fix HiDPI-scaling of fonts.
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        developed_res_x = DEV_WIDTH
        developed_res_y = DEV_HEIGHT
        multiplier = screen_width / developed_res_x
        global HEADING_SIZE  # Mandate reference to global constant
        global BUTTON_SIZE
        global STATUS_SIZE
        HEADING_SIZE = int(HEADING_SIZE / multiplier)
        BUTTON_SIZE = int(BUTTON_SIZE / multiplier)
        STATUS_SIZE = int(STATUS_SIZE / multiplier)
        print(str(screen_width) + str(screen_height))
        self.root.geometry(str(int(WIDTH/multiplier)) +
                           "x" + str(int(HEIGHT/multiplier)))

        # Begin defining instance variables
        self.root.title("Yonder Arctic OPS")
        self.in_q = in_q  # Messages sent here from base_station.py
        self.out_q = out_q  # Messages sent to base_station.py
        self.top_frame = Frame(self.root, bd=1)
        self.top_frame.pack(fill=BOTH, side=TOP,
                            padx=MAIN_PAD_X, pady=MAIN_PAD_Y, expand=YES)

        self.bot_frame = Frame(self.root, bd=1)
        self.bot_frame.pack(fill=BOTH, side=BOTTOM,
                            padx=MAIN_PAD_X, pady=MAIN_PAD_Y, expand=YES)

        self.init_function_frame()
        self.init_map_frame()
        self.init_status_frame()
        self.init_calibrate_frame()
        self.init_log_frame()
        self.init_mission_frame()
        self.create_map(self.map_frame)
        self.create_function_buttons()

        # Call function to properly end the program
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.update_idletasks()
        self.root.update()

        # Loop that checks our in-queue tasks given from the BaseStation object
        self.root.after(REFRESH_TIME, self.check_tasks)
        # Begin running GUI loop
        self.root.mainloop()

    def check_tasks(self):
        """ Evaluates the commands/tasks given to us in the in-queue. These commands are 
        Passed as basic string objects. """
        while (self.in_q.empty() is False):
            eval(self.in_q.get())

        self.root.after(REFRESH_TIME, self.check_tasks)

    def get_time(self, now):
        return now.strftime("%Y-%m-%d %H:%M:%S: ")

    def init_function_frame(self):
        """ Creates the frame for all UI functions. """
        self.functions_frame = Frame(
            self.top_frame, height=TOP_FRAME_HEIGHT, width=150, bd=1, relief=SUNKEN)
        self.functions_frame.pack(
            padx=MAIN_PAD_X, pady=MAIN_PAD_Y, side=LEFT, fill=Y, expand=NO)
        self.functions_frame.pack_propagate(0)

    def init_map_frame(self):
        """ Create the frame for the x, y map """

        self.map_frame = Frame(self.top_frame, height=TOP_FRAME_HEIGHT,
                               width=TOP_FRAME_HEIGHT, bd=1, relief=SUNKEN)
        self.map_frame.pack(fill=BOTH, padx=MAIN_PAD_X,
                            pady=MAIN_PAD_Y, side=LEFT, expand=YES)
        self.map_frame.pack_propagate(0)

    def init_status_frame(self):
        self.status_frame = Frame(
            self.top_frame, height=TOP_FRAME_HEIGHT, width=350, bd=1, relief=SUNKEN)
        self.status_frame.pack(fill=BOTH, padx=MAIN_PAD_X,
                               pady=MAIN_PAD_Y, side=LEFT, expand=NO)
        self.status_frame.pack_propagate(0)
        self.status_label = Label(
            self.status_frame, text="Vehicle Stats", font=(FONT, HEADING_SIZE))
        self.status_label.pack()
        self.status_label.place(relx=0.22, rely=0.02)

        self.position_label_string = StringVar()
        self.position_label = Label(self.status_frame, textvariable=self.position_label_string, font=(
            FONT, STATUS_SIZE), justify=LEFT)
        self.position_label.pack()
        self.position_label_string.set("Position \n \tX: \t Y: ")
        self.position_label.place(relx=0.05, rely=0.30, anchor='sw')

        self.heading_label_string = StringVar()
        self.heading_label = Label(self.status_frame, textvariable=self.heading_label_string, font=(
            FONT, STATUS_SIZE), justify=LEFT)
        self.heading_label.pack()
        self.heading_label_string.set("Heading: ")
        self.heading_label.place(relx=0.05, rely=0.40, anchor='sw')

        self.battery_status_string = StringVar()
        self.battery_voltage = Label(
            self.status_frame, textvariable=self.battery_status_string, font=(FONT, STATUS_SIZE))
        self.battery_voltage.pack()
        self.battery_status_string.set("Battery Voltage: ")
        self.battery_voltage.place(relx=0.05, rely=0.50, anchor='sw')

        self.vehicle_status_string = StringVar()
        self.vehicle_status = Label(
            self.status_frame, textvariable=self.vehicle_status_string, font=(FONT, STATUS_SIZE))
        self.vehicle_status.pack()
        self.vehicle_status_string.set("Vehicle Status: Manual Control")
        self.vehicle_status.place(relx=0.05, rely=0.60, anchor='sw')

        self.comms_status_string = StringVar()
        self.comms_status = Label(
            self.status_frame, textvariable=self.comms_status_string, font=(FONT, STATUS_SIZE))
        self.comms_status.pack()
        self.comms_status_string.set("Comms Status: Not connected")
        self.comms_status.place(relx=0.05, rely=0.70, anchor='sw')

        # self.calibrate_xbox_button           = Button(self.status_frame, text = "Calibrate Controller", takefocus = False, width = BUTTON_WIDTH + 10, height = BUTTON_HEIGHT,
        #                                      padx = BUTTON_PAD_X, pady = BUTTON_PAD_Y, font = (FONT, BUTTON_SIZE), command = self.base_station.calibrate_controller )
        # self.calibrate_xbox_button.pack()
        #self.calibrate_xbox_button.place(relx = 0.05, rely = 0.80);
        # self.establish_comm_button           = Button(self.status_frame, text = "Connect to AUV", takefocus = False, width = BUTTON_WIDTH, height = BUTTON_HEIGHT,
        #                                       padx = BUTTON_PAD_X, pady = BUTTON_PAD_Y, font = (FONT, BUTTON_SIZE), command = self.base_station.calibrate_communication )
        # self.establish_comm_button.pack()
        #self.establish_comm_button.place(relx = 0.05, rely = 0.90);

    def init_log_frame(self):
        self.log_frame = Frame(
            self.bot_frame, height=BOT_FRAME_HEIGHT, width=700, bd=1, relief=SUNKEN)
        self.log_frame.pack(fill=BOTH, padx=MAIN_PAD_X,
                            pady=MAIN_PAD_Y, side=LEFT, expand=YES)
        self.log_frame.pack_propagate(0)
        self.console = Text(self.log_frame, font=(
            FONT, BUTTON_SIZE), state=DISABLED, width=700)

        self.scrollbar = Scrollbar(self.log_frame)
        self.console.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.console.pack()

    def log(self, string):
        time = self.get_time(datetime.datetime.now())
        self.console.config(state=NORMAL)
        self.console.insert(END, time + string + "\n")
        self.console.config(state=DISABLED)

    def init_calibrate_frame(self):
        self.calibrate_frame = Frame(
            self.bot_frame, height=BOT_FRAME_HEIGHT, width=350, bd=1, relief=SUNKEN)
        self.calibrate_frame.pack(
            fill=Y, padx=MAIN_PAD_X, pady=MAIN_PAD_Y, side=LEFT, expand=NO)
        self.calibrate_frame.pack_propagate(0)

        self.calibrate_label = Label(
            self.calibrate_frame, text="Motor Calibration", takefocus=False, font=(FONT, HEADING_SIZE))
        self.calibrate_label.grid(row=0, columnspan=3, sticky=W+E)

        self.left_calibrate_button = Button(self.calibrate_frame, text="LEFT", takefocus=False,  # width = 15, height = 3,
                                            padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(
                                                FONT, BUTTON_SIZE),
                                            )  # command = lambda: self.base_station.set_calibrate_flag(0) )

        self.left_calibrate_button.grid(row=2, column=0, pady=CALIBRATE_PAD_Y)

        self.right_calibrate_button = Button(self.calibrate_frame, text="RIGHT", takefocus=False,  # width = 15, height = 3,
                                             padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(
                                                 FONT, BUTTON_SIZE),
                                             )  # command = lambda: self.base_station.set_calibrate_flag(1) )

        self.right_calibrate_button.grid(row=2, column=2, pady=CALIBRATE_PAD_Y)

        self.front_calibrate_button = Button(self.calibrate_frame, text="FRONT", takefocus=False,  # width = 15, height = 3,
                                             padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(
                                                 FONT, BUTTON_SIZE),
                                             )  # command = lambda: self.base_station.set_calibrate_flag(2) )

        self.front_calibrate_button.grid(row=1, column=1, pady=CALIBRATE_PAD_Y)

        self.calibrate_all_button = Button(self.calibrate_frame, text="ALL", takefocus=False,  # width = 15, height = 3,
                                           padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(
                                               FONT, BUTTON_SIZE),
                                           )  # command = lambda: self.base_station.set_calibrate_flag(4) )

        self.calibrate_all_button.grid(row=2, column=1, pady=CALIBRATE_PAD_Y)

        self.back_calibrate_button = Button(self.calibrate_frame, text="Back", takefocus=False,  # width = 15, height = 3,
                                            padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(
                                                FONT, BUTTON_SIZE),
                                            )  # command = lambda: self.base_station.set_calibrate_flag(3) )

        self.back_calibrate_button.grid(row=3, column=1, pady=CALIBRATE_PAD_Y)

    def init_mission_frame(self):
        self.mission_frame = Frame(
            self.bot_frame, height=BOT_FRAME_HEIGHT, width=400, bd=1, relief=SUNKEN)
        self.mission_frame.pack(fill=Y, padx=COMBO_PAD_X,
                                pady=COMBO_PAD_Y, side=LEFT, expand=NO)
        self.mission_frame.pack_propagate(0)

        self.mission_list = Combobox(self.mission_frame, values=MISSIONS)
        self.mission_list.pack(expand=YES, fill=X, pady=COMBO_PAD_Y)
        #self.mission_list.bind("<<ComboboxSelected>>", lambda _ : out_q.put(missions.index(self_mission_list.get())))

    def abort_mission(self):
        ans = messagebox.askquestion(
            "Abort Mission", "Are you sure you want to abort the mission")
        if ans == 'yes':
            message = "Mission aborted"
            self.log(message)
        else:
            message = "Clicked mission abort; continuing mission though"
            self.log(message)

    def create_function_buttons(self):
        self.origin_button = Button(self.functions_frame, text="Set Origin", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                    padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=self.map.new_waypoint_prompt)
        self.add_waypoint_button = Button(self.functions_frame, text="Add Waypoint", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                          padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=self.map.new_waypoint_prompt)
        self.nav_to_waypoint_button = Button(self.functions_frame, text="Nav. to Waypoint", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                             padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=lambda: None)
        self.switch_to_manual_button = Button(self.functions_frame, text="Switch to Manual", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                              padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=lambda: None)
        self.stop_manual_button = Button(self.functions_frame, text="Stop Manual", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                         padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=lambda: None)
        self.abort_button = Button(self.functions_frame, text="ABORT MISSION", takefocus=False, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                   padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, bg='dark red', activebackground="red", overrelief="sunken", font=(FONT, BUTTON_SIZE), command=self.abort_mission)

        self.origin_button.pack(expand=YES, fill=X)
        self.add_waypoint_button.pack(expand=YES, fill=X)
        self.nav_to_waypoint_button.pack(expand=YES, fill=X)
        self.switch_to_manual_button.pack(expand=YES, fill=X)
        self.stop_manual_button.pack(expand=YES, fill=X)
        self.abort_button.pack(expand=YES, fill=X)

    def create_map(self, frame):
        self.map = Map(frame, self)
        self.zoom_in_button = Button(self.map_frame, text="+", takefocus=False, width=1, height=1,
                                     padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=self.map.zoom_in)
        self.zoom_in_button.place(relx=1, rely=0.0, anchor=NE)

        self.zoom_out_button = Button(self.map_frame, text="-", takefocus=False, width=1, height=1,
                                      padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y, font=(FONT, BUTTON_SIZE), command=self.map.zoom_out)
        self.zoom_out_button.place(relx=1, rely=0.06, anchor=NE)

    def on_closing(self):
        #    self.map.on_close()
        self.root.destroy()
        sys.exit()


# Define the window object.
'''root = Tk()
root.geometry("1400x800") 

# To fix HiDPI-scaling of fonts.
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
developed_res_x = 1920.0
developed_res_y = 1080.0
multiplier = screen_width / developed_res_x
HEADING_SIZE = int(HEADING_SIZE / multiplier)
BUTTON_SIZE  = int(BUTTON_SIZE  / multiplier)
STATUS_SIZE  = int(STATUS_SIZE  / multiplier)
 
# Create the main window.
Main = Main(root, bs)
# Call function to properly end the program
root.protocol("WM_DELETE_WINDOW", Main.on_closing)
root.update_idletasks()
root.update()
radio_connected = False

root.mainloop()
'''
