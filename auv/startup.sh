#!/bin/bash
sudo killall pigpiod
sudo pigpiod
sudo python3 -B auv.py
