#!/usr/bin/python
"""
Summary: We wish to control a magnetic field generator
using a custom high speed motor driver.
This example will scan a range of frequencies and phase
relationships along 3 axes (X, Y, Z).

A Silicon Labs Si5351 programable clock generator and
custom designed frequency indendendent digital phase shifter is used.

Author Peter Sichel
Copyright (c) 2018, Sustainable Softworks Inc
MIT Open Source License
https://opensource.org/licenses/MIT
"""

import atexit
import os
import threading
import time

import RPi.GPIO as GPIO

from PhaseShifter import PhaseShifter
from Si5351_clock import Si5351
from mag_sensor import MagneticSensor
from mag_scan_info import ScanInfo

GPIO.setwarnings(False)

ENABLE_X = 7
ENABLE_Y = 8
ENABLE_Z = 25
IN_X = 16
IN_Y = 20
IN_Z = 21
MAG_READY_PIN = 5

# Pin Setup:
GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme.
GPIO.setup(ENABLE_X, GPIO.OUT)  # Red LED pin set as output
GPIO.setup(ENABLE_Y, GPIO.OUT)  # Yellow LED pin set as output
GPIO.setup(ENABLE_Z, GPIO.OUT)  # Green LED pin set as output
GPIO.setup(IN_X, GPIO.OUT)  # Red LED pin set as output
GPIO.setup(IN_Y, GPIO.OUT)  # Yellow LED pin set as output
GPIO.setup(IN_Z, GPIO.OUT)  # Green LED pin set as output


# recommended for auto-disabling magnets on shutdown!
def turn_off_magnets():
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)
    GPIO.output(IN_X, False)
    GPIO.output(IN_Y, False)
    GPIO.output(IN_Z, False)


atexit.register(turn_off_magnets)


# call function after a delay
def callMethodWithParamsAfterDelay(method=None, params=[], seconds=0.0):
    return threading.Timer(seconds, method, params).start()


def cancelDelayedCall(inTimer):
    inTimer.cancel()


### Support
def setClocks(fX, fY, fZ, si):
    # If we always use pll A, don't want to keep reseting it.
    pll = 0
    if (fX > 0):
        si.setFrequency(clock=0, pll=pll, targetFrequency=fX)  # X axis
    else:
        si.disableOutput(0)  # disable clock 0
    if (fY > 0):
        si.setFrequency(clock=1, pll=pll, targetFrequency=fY)  # Y axis
    else:
        si.disableOutput(1)  # disable clock 1
    if (fZ > 0):
        si.setFrequency(clock=2, pll=pll, targetFrequency=fZ)  # Z axis
    else:
        si.disableOutput(2)  # disable clock 2


def setPhase1(paramsD):
    # Clock signals 1 and 2 are set to 180 times the base frequency (Clk0)
    # and then counted down to adjust the phase.
    # The clock phase parameter is in degrees 0 to 360. 
    # Odd values invert the clock to shift a half cycle.
    phaseShifterIO_Clk1 = paramsD['phaseShifterIO_Clk1']
    degrees = paramsD['phaseClk1']
    si = paramsD['si']

    offset = degrees / 2
    invert = degrees % 2
    turnOnAt = offset % 240
    turnOffAt = (offset + 120) % 240  # +120 is 50% duty cycle of 240
    phaseShifterIO_Clk1.setA(turnOnAt)
    phaseShifterIO_Clk1.setB(turnOffAt)
    if (invert):
        si.invertOutput(invert=True, channel=1)


def setPhase2(paramsD):
    # Clock signals 1 and 2 are set to 180 times the base frequency (Clk0)
    # and then counted down to adjust the phase.
    # The clock phase parameter is in degrees 0 to 360. 
    # Odd values invert the clock to shift a half cycle.
    phaseShifterIO_Clk2 = paramsD['phaseShifterIO_Clk2']
    degrees = paramsD['phaseClk2']
    si = paramsD['si']

    offset = degrees / 2
    invert = degrees % 2
    turnOnAt = offset % 240
    turnOffAt = (offset + 120) % 240
    phaseShifterIO_Clk2.setA(turnOnAt)
    phaseShifterIO_Clk2.setB(turnOffAt)
    if (invert):
        si.invertOutput(invert=True, channel=2)


### Test Cases
def test_1(paramsD):
    # scan frequencies on one or more axis
    if (paramsD['index'] == 0):
        print('Initialize for test_1')
        paramsD['fBase'] = 20000
        paramsD['fDelta'] = 2
        paramsD['fEnd'] = 50000
    # set frequencies, 0=off
    fBase = paramsD['fBase']
    fX = 0
    fY = fBase
    fZ = 0
    paramsD['fX'] = fX
    paramsD['fY'] = fY
    paramsD['fZ'] = fZ
    si = paramsD['si']
    setClocks(fX, fY, fZ, si)


def test_2(paramsD):
    # scan frequencies on two axis with inverted clocks and offset
    index = paramsD['index']
    if (index == 0):
        print('Initialize for test_2')
        turn_off_magnets()
        paramsD['fStart'] = 22000
        paramsD['fEnd'] = 25000
        paramsD['fBase'] = paramsD['fStart']
        paramsD['fDelta'] = 1
        paramsD['phaseClk1'] = 0
        paramsD['phaseClk2'] = 0
        paramsD['durationStart'] = 1.0
        paramsD['durationEnd'] = 1.0
        paramsD['duration'] = paramsD['durationStart']
        paramsD['durationDelta'] = 0.010
        paramsD['space'] = 0.9
        paramsD['indexPrevious'] = 0  # print samples every N steps
    # set frequencies, 0=off
    fBase = paramsD['fBase']
    fX = fBase
    fY = 0
    fZ = fBase
    paramsD['fX'] = fX
    paramsD['fY'] = fY
    paramsD['fZ'] = fZ
    si = paramsD['si']
    setClocks(fX, fY * 240, fZ * 240, si)
    # si.invertOutput(invert=True, channel=0)
    setPhase1(paramsD)
    setPhase2(paramsD)
    # GPIO.output(IN_Y, False)
    # GPIO.output(ENABLE_Y, True)


def test_3(paramsD):
    # scan with harmonics
    if (paramsD['index'] == 0):
        print('Initialize for test_3')
        paramsD['fBase'] = 50000
        paramsD['fDelta'] = 2
        paramsD['fEnd'] = 150000
        paramsD['duration'] = 0.5
        paramsD['durationEnd'] = 0.5
    # set frequencies, 0=off
    fBase = paramsD['fBase']
    fX = 3 * fBase
    fY = 3 * fBase
    fZ = fBase
    paramsD['fX'] = fX
    paramsD['fY'] = fY
    paramsD['fZ'] = fZ
    si = paramsD['si']
    setClocks(fX, fY, fZ, si)
    si.invertOutput(invert=True, channel=1)


### scanning sequence
def sendBurst(paramsD):
    # initiate burst for selected test
    test_2(paramsD)
    duration = paramsD['duration']
    mSec = duration - 0.001  # setup to read sensor 1ms before end of burst
    # chain for next step
    callMethodWithParamsAfterDelay(method=readSensor1, params=[paramsD], seconds=mSec)


def readSensor1(paramsD):
    # read MAG3110 sensor to initialize for a new measurement
    magSample = paramsD['mag'].readMagneticField()
    paramsD['doReadSensor'] = True  # read again when ready interrupt fires
    magSample['fX'] = paramsD['fX']
    magSample['fY'] = paramsD['fY']
    magSample['fZ'] = paramsD['fZ']
    # chain for next step after 1ms to finish burst interval
    callMethodWithParamsAfterDelay(method=endBurst, params=[paramsD], seconds=0.001)


def endBurst(paramsD):
    si.enableOutputs(False)
    space = paramsD['space']  # space between bursts
    # callMethodWithParamsAfterDelay(method=readSensor2, params=[paramsD], seconds=0.012)
    callMethodWithParamsAfterDelay(method=updateParameters, params=[paramsD], seconds=space)


def readSensor2(paramsD):
    # print("readSensor2")
    magSample = paramsD['mag'].readMagneticField()
    magSample['fX'] = paramsD['fX']  # include frequency with sample
    magSample['fY'] = paramsD['fY']
    magSample['fZ'] = paramsD['fZ']
    magSample['fBase'] = paramsD['fBase']
    magSample['duration'] = paramsD['duration']
    magSamples = paramsD['magSamples']
    magSamples.append(magSample)
    index = paramsD['index']
    indexPrevious = paramsD['indexPrevious']
    if (index - indexPrevious > 10):
        # print(magSample)
        offset = float(paramsD['phaseClk1']) * 180 / 240
        print('duration:%.2f,fX:%d, fY:%d, fZ:%d, magX:%d, magY:%d, magZ:%d' % (
        magSample['duration'], magSample['fX'], magSample['fY'], magSample['fZ'],
        magSample['x'], magSample['y'], magSample['z']))
        print('phase1:%.2f degrees\n' % (offset))
        paramsD['indexPrevious'] = index
    # updateParameters(paramsD)


def updateParameters(paramsD):
    # Get current parameters
    fBase = paramsD['fBase']  # frequency
    fDelta = paramsD['fDelta']  # delta frequency increment amount
    phaseClk1 = paramsD['phaseClk1']
    phaseClk2 = paramsD['phaseClk2']
    duration = paramsD['duration']
    durationDelta = paramsD['durationDelta']
    index = paramsD['index']
    index += 1
    paramsD['index'] = index
    # not updated
    fStart = paramsD['fStart']
    fEnd = paramsD['fEnd']
    durationStart = paramsD['durationStart']
    durationEnd = paramsD['durationEnd']

    phaseClk1 += 1
    phaseClk2 += 1
    if (phaseClk2 < 240):
        # For this test, we only need to shift 180 degrees
        # to cover every phase relationship between two clock signals
        # Note we doulbe the number of counts per cycle by inverting 
        # the clock every other step.
        callMethodWithParamsAfterDelay(method=sendBurst, params=[paramsD], seconds=0.001)

    elif (duration < durationEnd):
        duration += durationDelta
        # repeat burst sequence
        callMethodWithParamsAfterDelay(method=sendBurst, params=[paramsD], seconds=0.001)
    else:
        duration = durationStart
        if (fBase < fEnd):
            fBase += fDelta
            # repeat burst sequence after 1ms
            callMethodWithParamsAfterDelay(method=sendBurst, params=[paramsD], seconds=0.001)
        else:
            paramsD['loop'] = False
            print('Sequence completed')
    # save updated parameters
    paramsD['fBase'] = fBase
    paramsD['duration'] = duration
    paramsD['phaseClk1'] = phaseClk1 % 240
    paramsD['phaseClk2'] = phaseClk2 % 240

    if (index % 1000 == 0) or (paramsD['loop'] == False):
        # saveSamples(paramsD)
        magSamples = paramsD['magSamples']
        magSamples = []
        paramsD['magSamples'] = magSamples
        print('Mag samples cleared')


def saveSamples(paramsD):
    # Save the data we collected
    magSamples = paramsD['magSamples']
    fh = open('mag_profile.csv', 'a')
    for magSample in magSamples:
        fh.write('%d,%.2f,%d,%d,%d,%d,%d,%d\n' % (
        magSample['fBase'], magSample['duration'], magSample['fX'], magSample['fY'], magSample['fZ'],
        magSample['x'], magSample['y'], magSample['z']))
        # reset dictionary to collect more
        magSamples = []
        paramsD['magSamples'] = magSamples
    fh.close()
    print('file saved')


def mag_event_callback(pin):
    # print("Mag Event")
    if (paramsD['doReadSensor']):
        paramsD['doReadSensor'] = False
        readSensor2(paramsD)


#
# Main Program to run test sequence
#
print("Start")
if os.path.isfile("mag_profile.csv"):
    os.remove("mag_profile.csv")
    print("Previous mag_profile.csv removed!")
si = Si5351()
mag = MagneticSensor()
phaseShifterIO_Clk1 = PhaseShifter()
phaseShifterIO_Clk2 = PhaseShifter(address=0x21)
magSamples = []
si.enableOutputs(False)  # turn off all outputs
paramsD = {'si': si, 'mag': mag, 'phaseShifterIO_Clk1': phaseShifterIO_Clk1, 'phaseShifterIO_Clk2': phaseShifterIO_Clk2,
           'phaseClk1': 0, 'phaseClk2': 0, 'durationStart': 0.050, 'durationEnd': 0.50,
           'fStart': 30000, 'fEnd': 40000,
           'index': 0, 'magSamples': magSamples, 'doReadSensor': False, 'loop': True}
scan_state = ScanInfo()
# paramsD is a dictionary of test parameters passed from step to step.
# This allows asynchronous processing and also simplifies specifying multiple tests compactly.
# si and mag are controller ojects for Si5351 clock generator and MAG3110 magnetic sensor
# fx, fy, fz are frequencies for each magnetic axis. 0 means disabled.
# fEnd is the ending frequency. If frequencies are looped, fStart is the current resume frequency.
# Duration is length of burst to send in seconds.
# DurationEnd allows incrementing pulse duration until a limit is reached.
# deltaX, deltaY, deltaZ (not specified here) is the frequency shift after each pulse sequence
# index counts each test cycle
# results are stored in array magSamples which is saved to disk periodically in file mag_profile.csv
# doReadSenor is used to control when a sensor interrupt will read the magnetic field strength.
# loop is used to indicate when the testing cycle has completed
# setup to read when MAG3110 is ready.
GPIO.setup(MAG_READY_PIN, GPIO.IN)  # MAG3110 ready interrupt
GPIO.add_event_detect(MAG_READY_PIN, GPIO.RISING, callback=mag_event_callback)
# GPIO.remove_event_detect(MAG_READY_PIN)
sendBurst(paramsD)

print("Press ^C to abort\n")
fh = open('mag_profile.csv', 'a')
fh.write("freq_base,duration,freq_x,freq_y,freq_z,mag_x,mag_y,mag_z\n")
fh.close()
while (paramsD['loop']):
    print('.')
    # check if we're done every 5 seconds
    time.sleep(5.0)

# cleanup
GPIO.remove_event_detect(MAG_READY_PIN)
si.enableOutputs(False)
GPIO.output(ENABLE_X, False)
GPIO.output(ENABLE_Y, False)
GPIO.output(ENABLE_Z, False)
print("End")
