from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor
from sensors import sgp30

addr = "0x39"

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        global SGPsensor
        self.name = "Light"
        self.unit = "lux"

        if SGPsensor:
            print("co2- it exists")
            self.sgpObject = SGPsensor
        else:
            print("co2- it doesn't exist")
            # If it doesn't exist, create it.
            # SGPsensor = sgp30.SGP30()
            # self.sgpObject = SGPsensor
        self.name = "co2"

    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgpObject.co2