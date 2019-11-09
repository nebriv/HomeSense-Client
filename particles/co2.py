from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor
from sensors import sgp30

addr = "0x39"
SGPsensor = sgp30.SGPsensor

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        global SGPsensor
        self.name = "CO2"
        self.unit = "ppm"

        print(SGPsensor.sensor_running)

        if SGPsensor.sensor_running:
            print("SPG Sensor Running")
            self.sgpObject = SGPsensor
        else:
            print("SPG Sensor not running")
            # If it doesn't exist, create it.
            # SGPsensor = sgp30.SGP30()
            # self.sgpObject = SGPsensor


    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgpObject.co2