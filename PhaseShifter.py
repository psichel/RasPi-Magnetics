#!/usr/bin/python
#
# PhaseShifter.py - Uses MCP23017 IO Expander to control a
# custom designed frequency independent digital phase shifter.
#
# Author: Peter Sichel 13-Jul-2019 
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT
#

from Adafruit_I2C import Adafruit_I2C
import time
from Si5351_clock import Si5351

# MCP23017 Datasheet
# http://ww1.microchip.com/downloads/en/DeviceDoc/20001952C.pdf

MCP23017_IODIRA = 0x00  # direction 0=output; 1=input;
MCP23017_IODIRB = 0x01
# MCP23017_IOCONA = 0x0A	# IO Control port A; POR (power on reset) = 0x00
# MCP23017_IOCONB = 0x0A	# IO Control port B; POR (power on reset) = 0x00
MCP23017_GPIOA = 0x12  # GPIO port A
MCP23017_GPIOB = 0x13  # GPIO port B
# MCP23017_GPPUA  = 0x0C	# GPIO Pull Up register port A
# MCP23017_GPPUB  = 0x0D	# GPIO Pull Up register port B
# MCP23017_OLATA  = 0x14	# Output Latch port A
# MCP23017_OLATB  = 0x15	# Output Latch port B


MCP23017_I2C_ADDRESS_DEFAULT = 0x20


class PhaseShifter(object):

    def __init__(self, address=MCP23017_I2C_ADDRESS_DEFAULT, busnum=-1):
        self.i2c = Adafruit_I2C(address=address, busnum=busnum)
        self.address = address
        # Configure as all outputs
        self.i2c.write8(MCP23017_IODIRA, 0x00)  # all outputs on port A
        self.i2c.write8(MCP23017_IODIRB, 0x00)  # all outputs on port B

    def set_a(self, value):
        self.i2c.write8(MCP23017_GPIOA, value & 0xFF)

    def set_b(self, value):
        self.i2c.write8(MCP23017_GPIOB, value & 0xFF)

    def set_phase_count240(self, phase_offset, clock_base, clock_output):
        # Phase shift the corresponding output clock relative to Clk0.
        # Assume the input clock is set to 240 times Clk0
        # 240 was chosen because our max 8-bit count is 256.
        # Assumes Clk1 and Clk2 are close to clock 0 since we only count up to 240.
        # We count the number of 240x pulses to turn the output clock on (A side) and off (B side).
        # The passed in phase shift is in counts of 240.
        turn_on_at = phase_offset % 240
        turn_off_at = (phase_offset + 120) % 240  # +120 is 50% duty cycle of 240
        self.set_a(turn_on_at)
        self.set_b(turn_off_at)
        # Imagine the desired output clock is 2x Clk0.
        # In this case counting 240x pulses will only let us turn on or off from 0-180 degrees of Clk0
        # The solutions is to set the input clock to 120x Clk0
        # so counting to 240 covers the entire range of Clk0.
        # As the desired output frequency increases relative to Clk0, we lower the clock multiplier.
        # The phase_offset parameter still specifies counts of 240.
        # We can calculate the best fit clock multiplier as
        clock_multiplier = 240  # default
        if clock_output != 0:  # clock_output 0 indicates clock is off
            clock_multiplier = int(float(clock_base) / float(clock_output) * 240)
            # Debug
            # print("\nset_phase_count240()")
            # print('phase_offset: %d, clock_base: %d, clock_output: %d' %(phase_offset, clock_base, clock_output))
            # print('turn_on_at: %d, turn_off_at: %d' %(turn_on_at, turn_off_at))
            # print('clock_multiplier: %d' %clock_multiplier)
        return clock_multiplier
        # Example: clock_base = 10_000, clock_output = 15_000
        # clock_multiplier = 160.  15_000 * 160 / 240 == 10_000

    def clock_disable(self):
        # Force the clock output to logical low value to turn off magnets.
        # turn_off_at 1, turn_on_at 255 which should never be reached.
        self.set_a(255)
        self.set_b(1)


def set_clocks(fx, fy, fz, clock_gen):
    # This is used for testing phase shifter behavior below.
    # The corresponding behavior is visible via the onboard LEDs.
    # If we always use pll A, don't want to keep resetting it.
    pll = 0
    if fx > 0:
        clock_gen.setFrequency(clock=0, pll=pll, targetFrequency=fx)  # X axis
    else:
        clock_gen.disableOutput(0)  # disable clock 0
    if fy > 0:
        clock_gen.setFrequency(clock=1, pll=pll, targetFrequency=fy)  # Y axis
    else:
        clock_gen.disableOutput(1)  # disable clock 1
    if fz > 0:
        clock_gen.setFrequency(clock=2, pll=pll, targetFrequency=fz)  # Z axis
    else:
        clock_gen.disableOutput(2)  # disable clock 2


if __name__ == '__main__':
    print("io_expander start")
    ioxAB = PhaseShifter()
    ioxCD = PhaseShifter(address=0x21)
    si = Si5351()

    # step through each phase at 1 second intervals
    # Observe the LEDs on Phase Shifter to verify count up, and relative brightness
    # of phase shifted outputs.
    # fX = 40000
    # fY = fX * 192
    # fZ = fX * 192
    # set_clocks(fX, fY, fZ, si)
    # for i in range(191):
    # 	#i = 2
    # 	# step through every phase: A=turn on count; B=turn off count
    # 	# clock1 = clock0 + 90 degrees
    # 	ioxAB.setA( i%192 )
    # 	ioxAB.setB( (i+96)%192 )	# 6 is 1/4 cycle at 24 increments per cycle
    #
    # 	ioxCD.setA( (i+48)%192 )
    # 	ioxCD.setB( (i+144)%192 )	# 6 is 1/4 cycle at 24 increments per cycle
    # 	time.sleep(1.0)

    # test A and B side of Flip Flop on
    # Observe output LEDs to verify flip flops toggle with 3 vs 1 second interval.
    # fX = 40000
    # fY = fX * 192
    # fZ = fX * 192
    # set_clocks(fX, fY, fZ, si)
    # for i in range(10):
    # 	ioxAB.setA(1)	# CLKs full on
    # 	ioxAB.setB(0)
    # 	ioxCD.setA(0)
    # 	ioxCD.setB(1)
    # 	time.sleep(3.0)
    # 	ioxAB.setA(0)	# - CLKs full on
    # 	ioxAB.setB(1)
    # 	ioxCD.setA(1)
    # 	ioxCD.setB(0)
    # 	time.sleep(1.0)

    # Test relative phasing
    # Observe how difference between phases changes relative output LEDs
    fX = 40000
    fY = fX * 192
    fZ = fX * 192
    set_clocks(fX, fY, fZ, si)
    for i in range(10):
        # all on
        ioxAB.set_a(72)  # Each different phase, lights on
        ioxAB.set_b(120)
        ioxCD.set_a(144)
        ioxCD.set_b(24)
        time.sleep(1.0)
        ioxAB.set_a(0)  # Same phase, light off
        ioxAB.set_b(96)
        ioxCD.set_a(0)
        ioxCD.set_b(96)
        time.sleep(3.0)

    print("io_expander done")
