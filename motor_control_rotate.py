#!/usr/bin/python
#
# Motor Control Program
# For use with Adafruit Motor HAT
# https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/installing-software#
#
# Summary: We wish to control a simple 2 wheel robot car
# with optical shaft encoders for sensing wheel movement.
# Building on the Adafruit Motor HAT library,
# we develop vehical movement routines from the
# real world problem domain.
#
# Proposed methods
# forward(speed, inches)
# reverse(speed, inches)
# turnLeft()
# turnRight()
#
# Author: Peter Sichel 12-Jan-2018
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT
#
import sys
from traffic_control import *
from wheel_movement import *

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import time, threading
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

SPEED_ENCODER_L = 5
SPEED_ENCODER_R = 6

# Pin Setup:
GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme. This uses the pin numbers that match the pin numbers on the Pi Traffic light.
GPIO.setup(SPEED_ENCODER_L, GPIO.IN)
GPIO.setup(SPEED_ENCODER_R, GPIO.IN)

traffic_L1 = piTrafficLight()

# wheel movement
wheel_L = wheelSensor(pin=SPEED_ENCODER_L)
wheel_R = wheelSensor(pin=SPEED_ENCODER_R)

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x6F)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
#    del wheel_L
#    del wheel_R
    traffic_L1.turnOffColor(GREEN)
    traffic_L1.turnOffColor(RED)

atexit.register(turnOffMotors)

# call function after a delay
def call_method_after_delay(method=None, params=[], seconds=0.0):
    return threading.Timer(seconds, method, params).start()

def cancel_delayed_call(inTimer):
    inTimer.cancel()

### Motor Control ###
motor_X = mh.getMotor(1)
motor_Y = mh.getMotor(2)
motor_Z = mh.getMotor(3)

def dirEast():
    motor_X.run(Adafruit_MotorHAT.FORWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(0)

def dirNorthEast():
    motor_X.run(Adafruit_MotorHAT.FORWARD)
    motor_Y.run(Adafruit_MotorHAT.FORWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(255)

def dirNorth():
    motor_Y.run(Adafruit_MotorHAT.FORWARD)
    motor_X.setSpeed(0)
    motor_Y.setSpeed(255)

def dirNorthWest():
    motor_X.run(Adafruit_MotorHAT.BACKWARD)
    motor_Y.run(Adafruit_MotorHAT.FORWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(255)

def dirWest():
    motor_X.run(Adafruit_MotorHAT.BACKWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(0)

def dirSouthWest():
    motor_X.run(Adafruit_MotorHAT.BACKWARD)
    motor_Y.run(Adafruit_MotorHAT.BACKWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(255)

def dirSouth():
    motor_Y.run(Adafruit_MotorHAT.BACKWARD)
    motor_X.setSpeed(0)
    motor_Y.setSpeed(255)

def dirSouthEast():
    motor_X.run(Adafruit_MotorHAT.FORWARD)
    motor_Y.run(Adafruit_MotorHAT.BACKWARD)
    motor_X.setSpeed(255)
    motor_Y.setSpeed(255)

def dirUp():
    motor_Z.run(Adafruit_MotorHAT.FORWARD)
    motor_Z.setSpeed(128)

def dirDown():
    motor_Z.run(Adafruit_MotorHAT.BACKWARD)
    motor_Z.setSpeed(128)

delay = 0.5
time.sleep(delay)

while (True):
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

    print ("Cycle")
    if delay > 0.06:
        delay = delay -0.05
    elif delay > 0.2:
        delay = delay -0.01

motor_X.run(Adafruit_MotorHAT.RELEASE)
motor_Y.run(Adafruit_MotorHAT.RELEASE)
traffic_L1.turnOffColor(GREEN)
traffic_L1.turnOffColor(RED)
