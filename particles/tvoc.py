from sensors.base_sensor import Sensor
from sensors import sgp30_sensor
import time

addr = 0x58
SGPsensor = sgp30_sensor.SGPsensor

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        global SGPsensor
        self.name = "TVoC"
        self.unit = "ppm"

        self.sgpObject = SGPsensor

    def setup(self):
        time.sleep(.1)
        if not self.sgpObject.sensor_running:
            self.sgpObject.setup()

    def get_name(self):
        return self.name

    def get_data(self):
        return sgp30_sensor.SGPsensor.tvoc