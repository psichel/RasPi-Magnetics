#!/usr/bin/python
#
# PhaseShifter.py - Uses MCP23017 IO Expander to control a
# custom designed frequency indendendent digital phase shifter.
#
# Author: Peter Sichel 13-Jul-2019 
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT
#

from Adafruit_I2C import Adafruit_I2C
import smbus
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

    def setA(self, value):
        self.i2c.write8(MCP23017_GPIOA, value & 0xFF)

    def setB(self, value):
        self.i2c.write8(MCP23017_GPIOB, value & 0xFF)


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
    # setClocks(fX, fY, fZ, si)
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
    # setClocks(fX, fY, fZ, si)
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
    setClocks(fX, fY, fZ, si)
    for i in range(10):
        # all on
        ioxAB.setA(72)  # Each different phase, lights on
        ioxAB.setB(120)
        ioxCD.setA(144)
        ioxCD.setB(24)
        time.sleep(1.0)
        ioxAB.setA(0)  # Same phase, light off
        ioxAB.setB(96)
        ioxCD.setA(0)
        ioxCD.setB(96)
        time.sleep(3.0)

print("io_expander done")
