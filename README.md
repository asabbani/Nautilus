# Origin
Repository for the [YonderDeep](https://www.yonderdeep.org/) 2019-2020 Origin AUV (Autonomous Underwater Vehicle) developed in the MESOM Laboratory at the Scripps Institution of Oceanography, UC San Diego for the research and study of global anthropogenic climate change.


## Basics
The codebase is split among two machines: 
  * a base station (a macOS / Linux machine)
  * Origin (an AUV with a Raspberry Pi 3 running Raspbian)

## Style Guidlines
Development will be done in Python3 using the [PEP8](https://pep8.org) style guidelines.
  * Uses spaces (4 per indentation) instead of tabs.
  * Utilizes the [autopep8](https://pypi.org/project/autopep8/0.8/extension) for automatic formatting.
  
Feel free to use the included settings.json file for VSCode development
  * Automatically enables autopep8 functionality with VSCode
  * Format-on-save enabled by default.
  * Python linting disabled by default. (a runtime language like python should not rely on linting)

# Base Station
This machine communicates with the AUV using radio communication. Its main role is selecting and beginning missions for the AUV. It also receives data wirelessly from the AUV and outputs to an in-house Python GUI.

## Hardware:
    Any Unix-like Machine (preferebly Ubuntu 16.04LTS+)
    A 915 MHz Radio
    Xbox 360 Controller

## System Dependencies:
    python3-tk (for use with tkinter UI development)
    python3-pip (enable pip package manager)
    xboxdrv (Xbox Controller Driver)
    gpsd
    gpsd-clients (for the cgps program, optional)

## Python Packages (in requirements.txt):
    tkinter
    matplotlib
    pyserial
    gps3
    screeninfo
    autopep8 (optional)

# Origin (the AUV)
A practical, 3D-printed multi-mission modular AUV, housing many sensors including pressure, audio (hydrophones), and GPS. It can also be adapted to implement sonar, salinity, PH, and temperature sensors.

## Hardware:
A fully assembled, 3D-printed Origin AUV also includes:

    Raspbery Pi 3 running Raspbian
    915 MHz Radio
    GPS Sensor
    Pressure sensor
    BNO055 IMU (intertial measurement unit)
    4 Underwater motors (Blue Robotics)
    Blue Robotics End-Caps
    Various acoustic acquisitions devives (made from ADC's and MCU's)

NOTE: that this does NOT include specialized YonderDeep PCBs, PDMs, batteries, or cables.

## System Dependencies:
    Python 3.5+ with pip
    gpsd
    gpsd-clients
    IMU Library/Drivers
    and many more...
This will continue to be updated as development continues.

## Python Packages (in requirements.txt):
    pyserial
    adafruit-circuitpython-bno055 (our Inertial Measurement Unit)
    and many more...
    
# Missions
The Origin AUV is designed to perform a wide variety of aquatic "missions", many of which involve the research and development of:

  * Underwater acoustic processing (acoustic)
  * Autonomous underwater navigation
  * Sonar echolocation 

# Development
Most development takes place at the MESOM Laboratory in the Scripps Institution of Oceanography at the University of California, San Diego. Due to the COVID-19 epidemic, software development will continue remotely for the forseeable future.

# Contributors
Kevin Medzorian,
Software Team Lead
* Computer Science
* UCSD Graduation: 2022


Ryan Xu,
Software Development
* Computer Science
* UCSD Graduation: 2022


Travis Davis,
Software Development
* Electrical Engineering
* UCSD Graduation: 2022


Stephen Boussarov,
Software Development
* Computer Science
* UCSD Graduation: 2022


Eric Estabaya,
Software Development
* Computer Science
* UCSD Graduation: 2022


Ethan Lew,
Software Development
* Mathematics-Computer Science
* UCSD Graduation: 2021
