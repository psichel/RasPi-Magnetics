#!/usr/bin/python
#
# Monitor Robot Car Speed Encoders
# In this example we use interrupts from the left and right wheel sensors
# to create a closed loop system where we can monitor the rotation of
# each wheel indepently.
#
# Author Peter Sichel 16-Sep-2018
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT
# 

import time, threading
import datetime
import math
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

SPEED_ENCODER_L = 5
SPEED_ENCODER_R = 6
DIAMETER = 2.625  # inches
CIRCUMFERENCE = 8.25
SLITS = 19
SLIT_DISTANCE = 0.434 # inches per slit transition


# Pin Setup:
GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme. This uses the pin numbers that match the pin numbers on the Pi Traffic light.
GPIO.setup(SPEED_ENCODER_L, GPIO.IN)
GPIO.setup(SPEED_ENCODER_R, GPIO.IN)

class wheelSensor:
    # model
    inputPin = 5
    distance = 0    # inches 
    speed = 0
    lastTime = datetime.datetime.now()

    def increment(self, pin):
        self.distance += SLIT_DISTANCE
        now = datetime.datetime.now()
        delta = now - self.lastTime
        self.speed = SLIT_DISTANCE * 1000000 / delta.microseconds
        self.lastTime = now

    def __init__(self, pin=5):
        self.inputPin = pin
        GPIO.setup(self.inputPin, GPIO.IN)
        # Wait for the input to go low, run the function when it does
        GPIO.add_event_detect(self.inputPin, GPIO.FALLING, callback=self.increment, bouncetime=20)
            # GPIO.remove_event_detect(self.inputPin)

    def __del__(self):
        GPIO.remove_event_detect(self.inputPin)

    def reset(self):
        self.distance = 0;
        self.speed = 0;
        self.lastTime = datetime.datetime.now() 
        print ("Distance reset to 0")

