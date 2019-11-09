from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor
from sensors import sgp30

addr = 0x58
SGPsensor = sgp30.SGPsensor

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        global SGPsensor
        self.name = "CO2"
        self.unit = "ppm"

        self.sgpObject = SGPsensor

            # If it doesn't exist, create it.
            # SGPsensor = sgp30.SGP30()
            # self.sgpObject = SGPsensor

    def setup(self):
        self.sgpObject.setup()

    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgpObject.co2