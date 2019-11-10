import time
import pigpio
import math
import binascii
from struct import unpack
from threading import Thread
#from .base_sensor import Sensor
import busio
import adafruit_sgp30
import board
import time
import board
import busio
import adafruit_sgp30

addr = 0x58

class SGP30():
    def __init__(self):
        global addr
        self.addr = addr
        self.sensor_running = False
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
        self.sgp30.iaq_init()

    def get_data(self):
        return(self.sgp30.eCO2, self.sgp30.TVOC)

    def run_sensor(self):
        pass

    def setup(self):
        if not self.sensor_running:
            print("Initializing SGP30 Sensor...")
            time.sleep(10)
            print("Sensor Started")

SGPsensor = SGP30()

