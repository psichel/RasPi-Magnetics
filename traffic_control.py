#!/usr/bin/python
#
# Traffic Light Control Program
# For use with LowVoltageLabs traffic light
# Pi-Traffic light installation
#   http://wiki.lowvoltagelabs.com/pitrafficlight
# Pi-Traffic light programming example
#    http://wiki.lowvoltagelabs.com/pitrafficlight_python_example
#
# Summary: There are 3 LEDs: Green, Yellow, and Red.
# We turn them on or off for various combinations and durations
#
# Author Peter Sichel
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT

import time, threading
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

# Pin Setup:
GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme. This uses the pin numbers that match the pin numbers on the Pi Traffic light.

ON = True
OFF = False
RED = 1
YELLOW = 2
GREEN = 3

# call function after a delay
def call_method_after_delay(method=None, params=[], seconds=0.0):
    return threading.Timer(seconds, method, params).start()

def cancel_delayed_call(inTimer):
    inTimer.cancel()

class piTrafficLight:
    # Model
    colorState = [0,0,0,0]
    blinkState = [0,0,0,0]
    sequenceState = 0
    sequenceInProgress = False
    sequenceTimer = None
    gpioRedPin = 9
    gpioYellowPin = 10
    gpioGreenPin = 11

    def __init__(self, redPin=9, yellowPin=10, greenPin=11):
        self.gpioRedPin     = redPin
        self.gpioYellowPin  = yellowPin
        self.gpioGreenPin   = greenPin
        GPIO.setup(redPin, GPIO.OUT)   # Red LED pin set as output
        GPIO.setup(yellowPin, GPIO.OUT)# Yellow LED pin set as output
        GPIO.setup(greenPin, GPIO.OUT) # Green LED pin set as output


    # Basic settings (On and Off)
    def setStateForColor(self, inState, inColor):
        # set traffic light
        if inState == ON:
            if inColor == RED:
                GPIO.output(self.gpioRedPin, True)
            elif inColor == YELLOW:
                GPIO.output(self.gpioYellowPin, True)
            elif inColor == GREEN:
                GPIO.output(self.gpioGreenPin, True)
        elif inState == OFF:
            if inColor == RED:
                GPIO.output(self.gpioRedPin, False)
            elif inColor == YELLOW:
                GPIO.output(self.gpioYellowPin, False)
            elif inColor == GREEN:
                GPIO.output(self.gpioGreenPin, False)
        # remember state
        self.colorState[inColor] = inState
        return

    def turnOffColor(self, inColor):
        self.setStateForColor(OFF, inColor)
        return

    def turnOnColor(self, inColor):
        self.setStateForColor(ON, inColor)
        return

    # Duration and Blinking
    def turnOnColorForDuration(self, inColor, inSeconds):
        self.turnOnColor(inColor)
        threading.Timer(inSeconds, self.turnOffColor, [inColor,inSeconds]).start()
        return

    def toggleColor(self, inColor):
        if self.colorState[inColor] == OFF:
            self.turnOnColor(inColor)
        else:
            self.turnOffColor(inColor)
        return

    def blinkColorWithDuration(self, inColor, inSeconds):
        if self.blinkState[inColor]==0:
            self.turnOffColor(inColor)
            return;
        self.toggleColor(inColor)
        threading.Timer(inSeconds, self.blinkColorWithDuration, [inColor,inSeconds]).start()
        return

    def startBlinkingColorWithDuration(self, inColor, inSeconds):
        if self.blinkState[inColor]==1:
            return
        self.blinkState[inColor] = 1
        self.blinkColorWithDuration(inColor, inSeconds)
        return

    def stopBlinkingColor(self, inColor):
        self.blinkState[inColor] = 0
        return

    # Sequence the traffic light using a function callback
    def turnOffColorWithCallbackAndParam(self, inColor, callback=None, sequenceState=0):
        self.setStateForColor(OFF, inColor)
        self.sequenceTimer = None
        if callback is not None:
            call_method_after_delay(callback, [sequenceState], 0)
        return

    def turnOnColorForDurationWithCallbackAndParam(self, inColor, inSeconds, callback=None, sequenceState=0):
        self.turnOnColor(inColor)
        self.sequenceTimer = call_method_after_delay(\
            self.turnOffColorWithCallbackAndParam,\
            [inColor, callback, sequenceState], inSeconds)
        return

    # Sequence traffic light Green-Yellow-Red until asked to stop
    def sequenceTrafficLight(self, sequenceState=0):
        if self.sequenceInProgress:
            if self.sequenceState==0:
                self.sequenceState += 1
                self.turnOnColorForDurationWithCallbackAndParam(GREEN, 2, self.sequenceTrafficLight, self.sequenceState)
            elif self.sequenceState==1:
                self.sequenceState += 1
                self.turnOnColorForDurationWithCallbackAndParam(YELLOW, 1, self.sequenceTrafficLight, self.sequenceState)
            elif self.sequenceState>=2:
                self.sequenceState = 0
                self.turnOnColorForDurationWithCallbackAndParam(RED, 2, self.sequenceTrafficLight, self.sequenceState) 
        return

    def startSequence(self):
        self.sequenceInProgress = True
        self.sequenceTrafficLight(0)
        return

    def stopSequence(self):
        self.sequenceInProgress = False
        if self.sequenceTimer is not None:
            self.sequenceTimer.cancel()
            self.turnOffColor(RED)
            self.turnOffColor(YELLOW)
            self.turnOffColor(GREEN)
        return


##==== Notes ====
## This program is intended to show well structured code and techniques.
## For those who may be learning:
## 1. The data model (program state) is clearly identified.
## 2. Each physical traffic light is represented by an instance of the
##    piTrafficLight class so it's easy to control more lights.
## 3. Hardware details are isolated or "hidden" from the rest of the program
##    so they can be updated (if needed) with minimal impact.
## 4. Each method name describes what it does and what parameters it uses.
## 5. Most methods implement a single concept from the real world
##    problem domain which makes them easy to understand and reason about.
## 6. Adheres to DRY principle (Don't Repeat Yourself).
## 7. Comments at the top of the file describe what the program does
##    and where to find related information.
