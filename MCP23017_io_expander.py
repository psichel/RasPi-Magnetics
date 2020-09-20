#!/usr/bin/python
#
# MCP23017 library for Raspberry Pi
# 16-Bit I2C I/O Expander
# In this example we use two I/O Expanders to control a Digital Phase Shifter
# applied to the output of an Si5351 digital clock generator.
#
# Author Peter Sichel
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT


from Adafruit_I2C import Adafruit_I2C
import smbus
import time
from Si5351_clock import Si5351

# MCP23017 Datasheet
# http://ww1.microchip.com/downloads/en/DeviceDoc/20001952C.pdf

MCP23017_IODIRA = 0x00		# Direction control 0=output; 1=input; 
MCP23017_IODIRB = 0x01
# MCP23017_IOCONA = 0x0A	# IO Control port A; POR (power on reset) = 0x00
# MCP23017_IOCONB = 0x0A	# IO Control port B; POR (power on reset) = 0x00
MCP23017_GPIOA  = 0x12		# GPIO port A
MCP23017_GPIOB  = 0x13		# GPIO port B
# MCP23017_GPPUA  = 0x0C	# GPIO Pull Up register port A
# MCP23017_GPPUB  = 0x0D	# GPIO Pull Up register port B
# MCP23017_OLATA  = 0x14	# Output Latch port A
# MCP23017_OLATB  = 0x15	# Output Latch port B

MCP23017_I2C_ADDRESS_DEFAULT = 0x20

class IOExpander(object):

	def __init__(self, address = MCP23017_I2C_ADDRESS_DEFAULT, busnum=-1):
		self.i2c = Adafruit_I2C(address=address, busnum=busnum)
		self.address = address
		# Configure as all outputs
		self.i2c.write8(MCP23017_IODIRA, 0x00)  # all outputs on port A
		self.i2c.write8(MCP23017_IODIRB, 0x00)  # all outputs on port B

	def setA(self, value):
		self.i2c.write8(MCP23017_GPIOA, value & 0xFF)

	def setB(self, value):
		self.i2c.write8(MCP23017_GPIOB, value & 0xFF)

def set_clocks(fX, fY, fZ, si):
	# If we always use pll A, don't want to keep reseting it.
	pll = 0
	if (fX > 0):
		si.setFrequency(clock=0, pll=pll, targetFrequency=fX)    # X axis
	else: si.disableOutput(0)  # disable clock 0 
	if (fY > 0):
		si.setFrequency(clock=1, pll=pll, targetFrequency=fY)    # Y axis
	else: si.disableOutput(1)  # disable clock 1 
	if (fZ > 0):
		si.setFrequency(clock=2, pll=pll, targetFrequency=fZ)   # Z axis
	else: si.disableOutput(2)  # disable clock 2 

if __name__ == '__main__':
	print ("io_expander start")
	ioxAB = IOExpander()
	ioxCD = IOExpander(address=0x21)
	si = Si5351()
	if (1): 
		fX = 8000
		fY = fX * 24
		fZ = fX * 24
		set_clocks(fX, fY, fZ, si)
		for i in range(23):
			#i = 2
			# step through every phase: A=turn on count; B=turn off count
			# clock1 = clock0 + 90 degrees
			ioxAB.setA( i%24 )
			ioxAB.setB( (i+12)%24 )	# 6 is 1/4 cycle at 24 increments per cycle

			ioxCD.setA( (i+6)%24 )
			ioxCD.setB( (i+18)%24 )	# 6 is 1/4 cycle at 24 increments per cycle
			time.sleep(1.0)

	if (0):
		fX = fY = fZ = 0
		set_clocks(fX, fY, fZ, si)
		ioxAB.set_a(0xAA)
		ioxAB.set_b(0xAA)	# 6 is 1/4 cycle at 24 increments per cycle

		ioxCD.set_a(0xAA)	# 48 is 90 degrees at 192 increments per cycle
		ioxCD.set_b(0xAA)
	print("io_expander done")
