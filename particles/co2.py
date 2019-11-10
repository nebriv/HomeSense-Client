from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor
from sensors import sgp30
import time

addr = 0x58

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        self.name = "CO2"
        self.unit = "ppm"

    def setup(self):
        pass

    def get_name(self):
        return self.name

    def get_data(self):
        return sgp30.SGPsensor.sgp30.eCO2