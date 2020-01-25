# Origin
Repository for the [YonderDeep](https://www.yonderdeep.org/) 2019-2020 Origin AUV (Autonomous Underwater Vehicle) developed in the MESOM Laboratory at the Scripps Institution of Oceanography, UC San Diego for the research and study of global anthropogenic climate change.


## Basics
The codebase is split among two machines: 
  * a base station (a macOS / Linux machine)
  * Origin (an AUV with a Raspberry Pi 3 running Raspbian)

## Development / Style Guidlines
Development will be done in Python3.
  * Indention will be mandated to 4 spaces, not tabs.
  * All files and methods need a descriptive header.
  * Else, follow the [PEP8](https://pep8.org) style guidelines.

# Base Station
This machine communicates with the AUV using radio communication. Its main role is selecting and beginning missions for the AUV. It also receives data wirelessly from the AUV and outputs to an in-house Python GUI.

## Hardware:
    Any Unix-like Machine (preferebly Ubuntu 16.04LTS+)
    A 915 MHz Radio
    Xbox 360 Controller

## System Dependencies:
    Python 3+ with pip
    xboxdrv (Xbox Controller Driver)

## Python Packages:
    Tkinter
    Matplotlib
    pyserial
    gps3

# Origin (the AUV)
A practical, 3D-printed multi-mission modular AUV, housing many sensors including pressure, audio (hydrophones), and GPS. However, it can also be adapted to implement Sonar, salinity, PH, and temperature sensors.

## Hardware:
A fully assembled, 3D-printed Origin AUV also includes:

    Raspbery Pi 3 running Raspbian
    915 MHz Radio
    GPS Sensor
    Pressure sensor
    4 Underwater motors (Blue Robotics)
    Blue Robotics End-Caps

Note that this does NOT include specialized YonderDeep PCBs, PDMs, batteries, or cables.

## System Dependencies:
    Python 3.7+ with pip
    and many more...
This will continue to be updated as development continues.

## Python Packages:
    pyserial
    and many more...
    
# Missions
The Origin AUV is designed to tackle many aquatic "missions" throughout its life, many of which involve the research and development of:

  * Underwater acoustic processing (acoustic)
  * Autonomous underwater navigation
  * Sonar echolocation 

# Development
Most development takes place at the MESOM Laboratory in the Scripps Institution of Oceanography at the University of California, San Diego.

