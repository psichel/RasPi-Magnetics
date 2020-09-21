#!/usr/bin/python
#
# Summary:
# Track state of test cycle while scanning.
#
# Author: Peter Sichel 9-Sep-2020
#


class ScanInfo(object):
    """This object allows us to pass all needed state between asynchronous
    test stages
    """
    def __init__(self):
        # which test to run
        self.test_config = None
        self.test_update_parameters = None

        # hardware device instances
        self.si = None
        self.mag_sensor = None
        self.phase_shifter1 = None
        self.phase_shifter2 = None

        # properties representing current test state
        self.frequency_start = 10000  # scan range start (Hz)
        self.frequency_end = 40000    # scan range end
        self.base_frequency = self.frequency_start  # the base frequency we're currently scanning
        self.offset_frequency = self.frequency_start   # offset from base for 2nd magnetic axis
        self.frequency_step = 1  # frequency step for subsequent scan
        self.clock1_phase_offset = 0  # initial phase for clock 1 (relative to clock 0)
        self.clock2_phase_offset = 0  # initial phase for clock 2 (relative to clock 0)
        self.duration_start = 1.0     # length of magnetic burst
        self.duration_end = 1.0       # we can step the duration from start to end if desired
        self.duration_now = self.duration_start
        self.duration_step = 0.010
        self.cycle_count = 0          # number of test cycles so far
        self.cycle_last_interval = 0  # Remember start of cycle interval
        self.cycle_pause = 0.9        # seconds before starting next cycle
        self.mag_samples = []         # frequency and magnetic field readings
        self.do_read_sensor = False   # read magnetic sensor
        self.run_next_test_cycle = True

        self.f0 = 0  # Clk0 frequency
        self.f1 = 0  # Clk1 frequency
        self.f2 = 0  # Clk2 frequency


class MagSample(object):
    """Magnetic field strenth readling along x, y, and z axis with corresponding frequency information"""
    def __init__(self, x, y, z):
        self.f0 = 0
        self.f1 = 0
        self.f2 = 0
        self.duration = 0
        self.base_frequency = 0
        self.call_method_after_delay = 0
        self.x = x
        self.y = y
        self.z = z
