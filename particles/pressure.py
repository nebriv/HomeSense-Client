# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# MPL3115A2
# This code is designed to work with the MPL3115A2_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/products

import time
import smbus

from sensors.base_sensor import Sensor
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create the logging file handler
fh = logging.FileHandler("homesense.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add handler to logger object
logger.addHandler(fh)


addr = 0x60

class Particle(Sensor):

    def __init__(self):
        Sensor.__init__(self)
        self.name = "Pressure"
        self.unit = "kPa"
        self.sensor_running = False


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

    def setup(self):
        try:
            self.bus = smbus.SMBus(1)
            self.sensor_running = True
        except Exception as err:
            logger.warning("Error starting %s: %s" % (self.name, err))

if __name__ == "__main__":
    test = Particle()
    test.setup()
    print(test.get_data())