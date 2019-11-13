# Raspberry Pi Driver for Adafruit HTU21D-F
# Go buy one at https://www.adafruit.com/products/1899
# written by D. Alex Gray dalexgray@mac.com
# Thanks to egutting at the adafruit.com forums
# Thanks to Joan on the raspberrypi.org forums
# This requires the pigpio library
# Get pigpio at http://abyz.co.uk/rpi/pigpio/index.html
#
# Copyright (c) 2014 D. Alex Gray
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math
import time
import board
import busio
from adafruit_htu21d import HTU21D

addr = 0x40

class HTU21DF():
    def __init__(self):
        global addr
        self.addr = addr
        self.sensor_running = False

    def run_sensor(self):
        pass

    def setup(self):
        if not self.sensor_running:
            print("Initializing HTU21DF Sensor")
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = HTU21D(i2c)
            self.sensor_running = True
            time.sleep(5)
            print("Sensor Started")

HTU21DFSensor = HTU21DF()