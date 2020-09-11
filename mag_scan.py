#!/usr/bin/python
"""
Summary: We wish to control a magnetic field generator
using a custom high speed motor driver.
This example will scan a range of frequencies and phase
relationships along 3 axes (X, Y, Z).

A Silicon Labs Si5351 programmable clock generator and
custom designed frequency independent digital phase shifter is used.

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
from mag_scan_info import ScanInfo, MagSample

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
def call_method_after_delay(method=None, params=None, seconds=0.0):
    if params is None:
        params = []
    return threading.Timer(seconds, method, params).start()


def cancel_delayed_call(timer):
    timer.cancel()


# = Support
def set_clocks(fx, fy, fz, si):
    # If we always use pll A, don't want to keep resetting it.
    pll = 0
    if fx > 0:
        si.setFrequency(clock=0, pll=pll, targetFrequency=fx)  # X axis
    else:
        si.disableOutput(0)  # disable clock 0
    if fy > 0:
        si.setFrequency(clock=1, pll=pll, targetFrequency=fy)  # Y axis
    else:
        si.disableOutput(1)  # disable clock 1
    if fz > 0:
        si.setFrequency(clock=2, pll=pll, targetFrequency=fz)  # Z axis
    else:
        si.disableOutput(2)  # disable clock 2


def set_phase1(scan_info):
    # Clock signals 1 and 2 are set to 180 times the base frequency (Clk0)
    # and then counted down to adjust the phase.
    # The clock phase parameter is in degrees 0 to 360. 
    # Odd values invert the clock to shift a half cycle.
    degrees = scan_info.clock1_phase_offset
    offset = degrees / 2
    invert = degrees % 2
    turn_on_at = offset % 240
    turn_off_at = (offset + 120) % 240  # +120 is 50% duty cycle of 240
    scan_info.phase_shifter1.setA(turn_on_at)
    scan_info.phase_shifter1.setB(turn_off_at)
    if invert:
        scan_info.si.invertOutput(invert=True, channel=1)


def set_phase2(scan_info):
    # Clock signals 1 and 2 are set to 180 times the base frequency (Clk0)
    # and then counted down to adjust the phase.
    # The clock phase parameter is in degrees 0 to 360. 
    # Odd values invert the clock to shift a half cycle.
    degrees = scan_info.clock2_phase_offset
    offset = degrees / 2
    invert = degrees % 2
    turn_on_at = offset % 240
    turn_off_at = (offset + 120) % 240
    scan_info.phase_shifter2.setA(turn_on_at)
    scan_info.phase_shifter2.setB(turn_off_at)
    if invert:
        scan_info.si.invertOutput(invert=True, channel=2)


# = Test Cases
def test_1(scan_info):
    # scan frequencies on one or more axis
    if scan_info.cycle_count == 0:
        print('Initialize for test_1')
        scan_info.base_frequency = 20000
        scan_info.frequency_step = 2
        scan_info.frequency_end = 50000
    # set frequencies, 0=off
    fx = 0
    fy = scan_info.base_frequency
    fz = 0
    scan_info.fx = fx
    scan_info.fy = fy
    scan_info.fz = fz
    set_clocks(fx, fy, fz, scan_info.si)


def test_2(scan_info):
    # scan frequencies on two axis with inverted clocks and offset
    if scan_info.cycle_count == 0:
        print('Initialize for test_2')
        turn_off_magnets()
        scan_info.frequency_start = 22000
        scan_info.frequency_end = 25000
        scan_info.base_frequency = scan_info.frequency_start
    # set frequencies, 0=off
    fx = scan_info.base_frequency
    fy = 0
    fz = scan_info.base_frequency
    scan_info.fx = fx
    scan_info.fy = fy
    scan_info.fz = fz
    set_clocks(fx, fy * 240, fz * 240, scan_info.si)
    # si.invertOutput(invert=True, channel=0)
    set_phase1(scan_info)
    set_phase2(scan_info)
    # GPIO.output(IN_Y, False)
    # GPIO.output(ENABLE_Y, True)


def test_3(scan_info):
    # scan with harmonics
    if scan_info.cycle_count == 0:
        print('Initialize for test_3')
        scan_info.base_frequency = 50000
        scan_info.frequency_step = 2
        scan_info.frequency_end = 150000
        scan_info.duration_now = 0.5
        scan_info.duration_end = 0.5
    # set frequencies, 0=off
    fx = 3 * scan_info.base_frequency
    fy = 3 * scan_info.base_frequency
    fz = scan_info.base_frequency
    scan_info.fx = fx
    scan_info.fy = fy
    scan_info.fz = fz
    set_clocks(fx, fy, fz, scan_info.si)
    scan_info.si.invertOutput(invert=True, channel=1)


# = scanning sequence
def send_burst(scan_info):
    # initiate burst for selected test
    test_2(scan_info)
    m_second = scan_info.duration_now - 0.001  # setup to read sensor 1ms before end of burst
    # chain for next step
    call_method_after_delay(method=read_sensor1, params=[scan_info], seconds=m_second)


def read_sensor1(scan_info):
    # read MAG3110 sensor to initialize for a new measurement
    x, y, z = scan_info.mag_sensor.readMagneticField()
    sample = MagSample(x, y, z)
    scan_info.do_read_sensor = True  # read again when ready interrupt fires
    sample.fx = scan_info.fx
    sample.fy = scan_info.fy
    sample.fz = scan_info.fz
    # chain for next step after 1ms to finish burst interval
    call_method_after_delay(method=end_burst, params=[scan_info], seconds=0.001)


def end_burst(scan_info):
    scan_info.si.enableOutputs(False)
    # call_method_after_delay(method=read_sensor2, params=[scan_info], seconds=0.012)
    call_method_after_delay(method=update_parameters, params=[scan_info], seconds=scan_info.cycle_pause)


def read_sensor2(scan_info):
    # print("read_sensor2")
    x, y, z = scan_info.mag_sensor.readMagneticField()
    sample = MagSample(x, y, z)
    sample.fx = scan_info.fx  # include frequency with sample
    sample.fy = scan_info.fy
    sample.fz = scan_info.fz
    sample.base_frequency = scan_info.base_frequency
    sample.duration = scan_info.duration_now
    scan_info.mag_samples.append(sample)
    if scan_info.cycle_count - scan_info.cycle_of_last_write > 10:
        # print(magSample)
        offset = float(scan_info.clock1_phase_offset) * 180 / 240
        print('duration:%.2f,fx:%d, fy:%d, fz:%d, magX:%d, magY:%d, magZ:%d' % (
            sample.duration, sample.fx, sample.fy, sample.fz,
            sample.x, sample.y, sample.z))
        print('phase1:%.2f degrees\n' % offset)
        scan_info.cycle_of_last_write = scan_info.cycle_count
    # update_parameters(scan_info)


def update_parameters(scan_info):
    scan_info.cycle_count += 1
    scan_info.clock1_phase_offset += 1
    scan_info.clock2_phase_offset += 1
    if scan_info.clock2_phase_offset < 240:
        # For this test, we only need to shift 180 degrees
        # to cover every phase relationship between two clock signals
        # Note we double the number of counts per cycle by inverting
        # the clock every other step.
        call_method_after_delay(method=send_burst, params=[scan_info], seconds=0.001)

    elif scan_info.duration_now < scan_info.duration_end:
        scan_info.duration_now += scan_info.duration_step
        # repeat burst sequence
        call_method_after_delay(method=send_burst, params=[scan_info], seconds=0.001)
    else:
        scan_info.duration_now = scan_info.duration_start
        if scan_info.base_frequency < scan_info.frequency_end:
            scan_info.base_frequency += scan_info.frequency_step
            # repeat burst sequence after 1ms
            call_method_after_delay(method=send_burst, params=[scan_info], seconds=0.001)
        else:
            scan_info['loop'] = False
            print('Sequence completed')
    # save updated parameters
    scan_info.clock1_phase_offset %= 240
    scan_info.clock2_phase_offset %= 240

    if (scan_info.cycle_count % 1000 == 0) or (not scan_info.run_next_test_cycle):
        save_samples(scan_info)


def save_samples(scan_info):
    # Save the data we collected
    samples = scan_info.mag_samples
    fh = open('mag_profile.csv', 'a')
    for sample in samples:
        fh.write('%d,%.2f,%d,%d,%d,%d,%d,%d\n' % (
            sample.base_frequency, sample.duration, sample.fx, sample.fy, sample.fz,
            sample.x, sample.y, sample.z))
        # reset samples array to collect more
        scan_info.mag_samples = []
    fh.close()
    print('file saved')


class ReadSensorEvents(object):
    def __init__(self, scan_info):
        self.scan_info = scan_info

    def setup(self):
        # Setup to read when MAG3110 is ready.
        GPIO.setup(MAG_READY_PIN, GPIO.IN)  # MAG3110 ready interrupt
        GPIO.add_event_detect(MAG_READY_PIN, GPIO.RISING, callback=self.callback)
        # GPIO.remove_event_detect(MAG_READY_PIN)

    def callback(self, pin):
        # print("Mag Event")
        if self.scan_info.do_read_sensor:
            self.scan_info.do_read_sensor = False
            read_sensor2(self.scan_info)

    def cleanup(self):
        GPIO.remove_event_detect(MAG_READY_PIN)

#
# Main Program to run test sequence


def prepare_test_run():
    # remove old data if any
    if os.path.isfile("mag_profile.csv"):
        os.remove("mag_profile.csv")
        print("Previous mag_profile.csv removed!")

    # write column headers to new csv output file
    fh = open('mag_profile.csv', 'a')
    fh.write("freq_base,duration,freq_x,freq_y,freq_z,mag_x,mag_y,mag_z\n")
    fh.close()


prepare_test_run()


def run_test_sequence():
    print("Starting test sequence")
    print("Press ^C to abort\n")
    scan_info = ScanInfo()
    # assign devices
    scan_info.si = Si5351()
    scan_info.mag_sensor = MagneticSensor()
    scan_info.phase_shifter1 = PhaseShifter()
    scan_info.phase_shifter2 = PhaseShifter(address=0x21)
    scan_info.mag_samples = []

    # scan_info is an object containing the test parameters we pass from step to step.
    # This allows asynchronous processing and also simplifies specifying multiple tests compactly.
    # si and mag are controller objects for Si5351 clock generator and MAG3110 magnetic sensor
    # fx, fy, fz are frequencies for each magnetic axis. 0 means disabled.
    # results are stored as an array of MagSample objects which is saved to disk periodically in file mag_profile.csv
    # see ScanInfo for a description of each parameter.

    read_events = ReadSensorEvents(scan_info)
    read_events.setup()

    send_burst(scan_info)
    while scan_info.run_next_test_cycle:
        print('.')  # let user know testing is underway
        # loop to check if we're done every 5 seconds
        time.sleep(5.0)

    # cleanup
    read_events.cleanup()
    scan_info.si.enableOutputs(False)
    GPIO.output(ENABLE_X, False)
    GPIO.output(ENABLE_Y, False)
    GPIO.output(ENABLE_Z, False)
    print("End")


run_test_sequence()
