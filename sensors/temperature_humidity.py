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
import time
import pigpio
import math
from threading import Thread
from .base_sensor import Sensor

class HTU21DF(Sensor):
    def __init__(self):
        super(Sensor, self).__init__()
        self.setup()

    def run_sensor(self):
        while True:
            handle = self.pi.i2c_open(self.bus, self.addr)  # open i2c bus
            self.pi.i2c_write_byte(handle, self.rdtemp)  # send read temp command
            time.sleep(.5)  # readings take up to 50ms, lets give it some time
            (count, byteArray) = self.pi.i2c_read_device(handle, 3)  # vacuum up those bytes
            t1 = byteArray[0]  # most significant byte msb
            t2 = byteArray[1]  # least significant byte lsb
            temp_reading = (t1 * 256) + t2  # combine both bytes into one big integer
            temp_reading = math.fabs(temp_reading)  # I'm an idiot and can't figure out any other way to make it a float
            self.temperature = ((temp_reading / 65536) * 175.72) - 46.85  # formula from datasheet
            time.sleep(1)
            self.pi.i2c_write_byte(handle, self.rdhumi)  # send read humi command
            time.sleep(.5)  # readings take up to 50ms, lets give it some time
            (count, byteArray) = self.pi.i2c_read_device(handle, 3)  # vacuum up those bytes
            self.pi.i2c_close(handle)  # close the i2c bus
            h1 = byteArray[0]  # most significant byte msb
            h2 = byteArray[1]  # least significant byte lsb
            humi_reading = (h1 * 256) + h2  # combine both bytes into one big integer
            humi_reading = math.fabs(humi_reading)  # I'm an idiot and can't figure out any other way to make it a float
            uncomp_humidity = ((humi_reading / 65536) * 125) - 6  # formula from datasheet
            # to get the compensated humidity we need to read the temperature
            time.sleep(1)
            self.humidity = ((25 - self.temperature) * -0.15) + uncomp_humidity
            #print(self.temperature)
            #print(self.humidity)


    def setup(self):
        print("Initializing HTU21DF Sensor")
        #print("RUNNING SETUP")
        self.pi = pigpio.pi()

        # HTU21D-F Address
        self.addr = 0x40

        # i2c bus, if you have a Raspberry Pi Rev A, change this to 0
        self.bus = 1

        # HTU21D-F Commands
        self.rdtemp = 0xE3
        self.rdhumi = 0xE5
        self.wtreg = 0xE6
        self.rdreg = 0xE7
        self.reset = 0xFE

        thread1 = Thread(target=self.run_sensor)
        thread1.daemon = True
        thread1.start()
        self.sensor_running = True
        time.sleep(5)
        print("Sensor Started")


    def htu_reset(self):
        handle = self.pi.i2c_open(self.bus, self.addr) # open i2c bus
        self.pi.i2c_write_byte(handle, self.reset) # send reset command
        self.pi.i2c_close(handle) # close i2c bus
        time.sleep(0.2) # reset takes 15ms so let's give it some time



HTU21DFSensor = None

class Temperature():
    def __init__(self):
        global HTU21DFSensor
        if HTU21DFSensor:
            #print("voc- it exists")
            self.sensorObject = HTU21DFSensor
        else:
            #print("voc- it doesn't exist")
            HTU21DFSensor = HTU21DF()
            self.sensorObject = HTU21DFSensor
        self.name = "temperature"
        self.unit = "fahrenheit"

    def get_name(self):
        return self.name

    def get_data(self):
        if self.unit == "celsius":
            return self.sensorObject.temperature
        elif  self.unit == "fahrenheit":
            temperature = 9.0 / 5.0 * self.sensorObject.temperature + 32
            return temperature


class Humidity():
    def __init__(self):
        global HTU21DFSensor
        if HTU21DFSensor:
            #print("voc- it exists")
            self.sensorObject = HTU21DFSensor
        else:
            #print("voc- it doesn't exist")
            HTU21DFSensor = HTU21DF()
            self.sensorObject = HTU21DFSensor
        self.name = "humidity"

    def get_name(self):
        return self.name

    def get_data(self):

        return self.sensorObject.humidity