#!/usr/bin/python
#
# Summary:
# Track state of test cycle while scanning.
#
# Author: Peter Sichel 9-Sep-2020
#
#
from mag_sensor import MagneticSensor
from Si5351_clock import Si5351
from PhaseShifter import PhaseShifter


class ScanInfo(object):
    """This object allows us to pass all needed state between asynchronous
    test stages
    """
    def __init__(self):
        # hardware device instances
        self.si = Si5351()
        self.mag_sensor = MagneticSensor()
        self.phase_shifter1 = PhaseShifter()
        self.phase_shifter2 = PhaseShifter(address=0x21)

        # properties representing current test state
        self.frequency_start = 10000  # original start_frequency (Hz)
        self.frequency_end = 40000
        self.frequency_current = self.frequency_start
        self.frequency_step = 1  # frequency step for subsequent scan
        self.clock1_phase_offset = 0  # initial phase for clock 1 (relative to clock 0)
        self.clock2_phase_offset = 0  # initial phase for clock 2 (relative to clock 0)
        self.duration_start = 1.0     # length of magnetic burst
        self.duration_end = 1.0       # we can step the duration from start to end if desired
        self.duration_current = self.duration_start
        self.duration_step = 0.010
        self.cycle_count = 0          # number of test cycles so far
        self.cycle_pause = 0.9        # seconds before starting next cycle
        self.mag_samples = []         # frequency and magnetic field readings
        self.do_read_sensor = False   # read magnetic sensor
        self.run_next_test_cycle = True
