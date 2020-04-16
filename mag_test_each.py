#!/usr/bin/python
#
# Summary: We wish to control a magnetic field generator
# using a custom high speed motor driver.
# This example is used to test each magnetic axis in sequence (X, Y, and Z)
#
# Author Peter Sichel 16-Sep-2018
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT
#
import sys
import atexit
import time, threading
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

ENABLE_X = 7
ENABLE_Y = 8
ENABLE_Z = 25
#ENABLE_X = 11
#ENABLE_Y = 9
#ENABLE_Z = 10
IN_X = 16
IN_Y = 20
IN_Z = 21

# Pin Setup:
GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme. This uses the pin numbers that match the pin numbers on the Pi Traffic light.
GPIO.setup(ENABLE_X, GPIO.OUT)   # Red LED pin set as output
GPIO.setup(ENABLE_Y, GPIO.OUT)# Yellow LED pin set as output
GPIO.setup(ENABLE_Z, GPIO.OUT) # Green LED pin set as output
GPIO.setup(IN_X, GPIO.OUT)   # Red LED pin set as output
GPIO.setup(IN_Y, GPIO.OUT)# Yellow LED pin set as output
GPIO.setup(IN_Z, GPIO.OUT) # Green LED pin set as output


# recommended for auto-disabling motors on shutdown!
def turnOffMagnets():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)

atexit.register(turnOffMagnets)

# call function after a delay
def callMethodWithParamsAfterDelay(method=None, params=[], seconds=0.0):
    return threading.Timer(seconds, method, params).start()

def cancelDelayedCall(inTimer):
    inTimer.cancel()


def dirEast():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, True)

def dirNorthEast():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, True)
    GPIO.output(IN_Y, True)

def dirNorth():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_Y, True)

def dirNorthWest():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, False)
    GPIO.output(IN_Y, True)

def dirWest():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, False)

def dirSouthWest():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, False)
    GPIO.output(IN_Y, False)

def dirSouth():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_Y, False)

def dirSouthEast():
    GPIO.output(ENABLE_X, True)
    GPIO.output(ENABLE_Y, True)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, True)
    GPIO.output(IN_Y, False)

def dirUp():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)    
    GPIO.output(ENABLE_Z, True)
    GPIO.output(IN_Z, True)

def dirDown():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)   
    GPIO.output(ENABLE_Z, True)
    GPIO.output(IN_Z, False)

def rotateCCW(delay = 0.5):
    dirUp()
    dirEast()
    time.sleep(delay)
    dirNorthEast()
    time.sleep(delay)

    dirNorth()
    time.sleep(delay)
    dirNorthWest()
    time.sleep(delay)

    dirDown()
    dirWest()
    time.sleep(delay)
    dirSouthWest()
    time.sleep(delay)

    dirSouth()
    time.sleep(delay)
    dirSouthEast()
    time.sleep(delay)
    dirEast()

def rotateCW(delay = 0.5):
    dirDown()
    dirEast()
    time.sleep(delay)
    dirSouthEast()
    time.sleep(delay)

    dirSouth()
    time.sleep(delay)
    dirSouthWest()
    time.sleep(delay)

    dirUp()
    dirWest()
    time.sleep(delay)
    dirNorthWest()
    time.sleep(delay)

    dirNorth()
    time.sleep(delay)
    dirNorthEast()
    time.sleep(delay)
    dirEast()

print("Start")
for i in range(10):
    print("Direction East")
    dirEast()
    time.sleep(5)
    print("Direction West")
    dirWest()
    time.sleep(5)
    print("Direction North")
    dirNorth()
    time.sleep(5)
    print("Direction South")
    dirSouth()
    time.sleep(5)
    print("Direction Up")
    dirUp()
    time.sleep(5)
    print("Direction Down")
    dirDown()
    time.sleep(5)

turnOffMagnets()
print("End")
