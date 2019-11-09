# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# MPL3115A2
# This code is designed to work with the MPL3115A2_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/products

#import smbus
import time
from sensors.base_sensor import Sensor

addr = "0x60"

class Particle(Sensor):

    def __init__(self):
        Sensor.__init__(self)
        self.name = "pressure"
        self.unit = "kPa"
        #self.bus = smbus.SMBus(1)
        self.bus = True

    def get_data(self):
        self.bus.write_byte_data(0x60, 0x26, 0x39)

        time.sleep(1)

        # MPL3115A2 address, 0x60(96)
        # Read data back from 0x00(00), 4 bytes
        # status, pres MSB1, pres MSB, pres LSB
        data = self.bus.read_i2c_block_data(0x60, 0x00, 4)

        # Convert the data to 20-bits
        pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
        pressure = (pres / 4.0) / 1000.0
        return pressure


