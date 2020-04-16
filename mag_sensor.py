#!/usr/bin/python
#
# MAG3110 magnetic field sensor (digital compass)
# This code is designed to work with the MAG3110_I2CS I2C Mini Module
# available from ControlEverything.com.
# https://www.controleverything.com/content/Compass?sku=MAG3110_I2CS#tabs-0-product_tabset-2
#
# Author Peter Sichel
# Copyright (c) 2018, Sustainable Softworks Inc
# MIT Open Source License
# https://opensource.org/licenses/MIT

from Adafruit_I2C import Adafruit_I2C
import time, threading
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
READY_PIN = 5

class MagneticSensor:

	def event_callback(self, pin):
		print("Mag Ready")
		if (self.doReadSensor):
			self.readMagneticField()
			#self.doReadSensor = False

	def __init__(self, readyPin=5, address=0x0E, busnum=-1):
		self.readyPin = readyPin
		self.address = address
		self.i2c = Adafruit_I2C(address=address, busnum=busnum)
		self.doReadSensor = True
			# MAG3110 config
		# CTRL_REG1 (0x10)  Value: 01
		#	Data rate 80 Hz, Over sampling rate 16, Active mode
		# CTRL_REG2 (0x11)  Value: 80
		#	Automatic Magnetic Sensor Reset enabled
		self.i2c.write8(0x10, 0x01)
		self.i2c.write8(0x11, 0x80)
		# setup to read when MAG3110 is ready.
        #GPIO.add_event_detect(self.readyPin, GPIO.RISING, callback=self.event_callback)
		# GPIO.remove_event_detect(READY_PIN)

	def __del__(self):
		##GPIO.remove_event_detect(READY_PIN)
		# MAG3110 CTRL_REG1 (0x10)  Value: 00
		#	Standby mode
		self.i2c.write8(0x10, 0x00)

	def readMagneticField(self):
		# Read data back from 0x01(1), 6 bytes
		# X-Axis MSB, X-Axis LSB, Y-Axis MSB, Y-Axis LSB, Z-Axis MSB, Z-Axis LSB
		try:
			data = self.i2c.readList(0x01, 6)

			# Convert the data
			xMag = data[0] * 256 + data[1]
			if xMag > 32767 :
				xMag -= 65536

			yMag = data[2] * 256 + data[3]
			if yMag > 32767 :
				yMag -= 65536

			zMag = data[4] * 256 + data[5]
			if zMag > 32767 :
				zMag -= 65536
		except:
			print("Failed to read from device")
			xMag = 0
			yMag = 0
			zMag = 0

		# Return field strength reading
		magSample = {'x':xMag, 'y':yMag, 'z':zMag}
		return magSample

		'''print ("Magnetic field in X-Axis : %d" %xMag)
		print ("Magnetic field in Y-Axis : %d" %yMag)
		print ("Magnetic field in Z-Axis : %d" %zMag)'''

if __name__ == '__main__':
		# Pin Setup:
	GPIO.setmode(GPIO.BCM)   # Broadcom pin-numbering scheme.
	GPIO.setup(READY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 	
	mag = MagneticSensor()
	GPIO.add_event_detect(READY_PIN, GPIO.RISING, callback=mag.event_callback)
	time.sleep(0.1)
	print ("main request")
	for i in range(20):
		mag.readMagneticField()
		print("\n")
		time.sleep(1.0)
	print ("mag_sensor done")
