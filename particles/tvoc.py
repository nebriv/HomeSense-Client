from sensors.base_sensor import Sensor
from sensors import sgp30_sensor
import time

addr = 0x58
sgp = sgp30_sensor.SGPsensor

class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        Sensor.__init__(self)
        self.name = "TVoC"
        self.unit = "ppm"

    def setup(self):
        time.sleep(.1)
        sgp.setup()

    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgp.tvoc