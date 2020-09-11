#!/usr/bin/python
#
# Summary: We wish to control a magnetic field generator
# using a custom high speed motor driver.
# This example turns off the magnet drivers.
#
# Author Peter Sichel
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT

import sys
import atexit
import time, threading
import RPi.GPIO as GPIO
from mag_sensor import MagneticSensor
from Si5351_clock import Si5351
GPIO.setwarnings(False)

ENABLE_X = 7
ENABLE_Y = 8
ENABLE_Z = 25
IN_X = 16
IN_Y = 20
IN_Z = 21
MAG_READY_PIN = 5

# Pin Setup:
GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme.
GPIO.setup(ENABLE_X, GPIO.OUT)   # Red LED pin set as output
GPIO.setup(ENABLE_Y, GPIO.OUT)# Yellow LED pin set as output
GPIO.setup(ENABLE_Z, GPIO.OUT) # Green LED pin set as output
GPIO.setup(IN_X, GPIO.OUT)   # Red LED pin set as output
GPIO.setup(IN_Y, GPIO.OUT)# Yellow LED pin set as output
GPIO.setup(IN_Z, GPIO.OUT) # Green LED pin set as output

# recommended for auto-disabling magnets on shutdown!
def turnOffMagnets():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)

atexit.register(turnOffMagnets)

# call function after a delay
def call_method_after_delay(method=None, params=[], seconds=0.0):
    return threading.Timer(seconds, method, params).start()

def cancel_delayed_call(inTimer):
    inTimer.cancel()


# cleanup
si = Si5351()
si.enableOutputs(False)
GPIO.output(ENABLE_X, False)
GPIO.output(ENABLE_Y, False)
GPIO.output(ENABLE_Z, False)
print("End")

