import time

from sensors import sgp30_sensor
from sensors.base_sensor import Sensor

addr = 0x58
sgp = sgp30_sensor.SGPsensor


class Particle(Sensor):
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        Sensor.__init__(self)
        global sgp
        self.name = "CO2"
        self.unit = "ppm"
        print("HELLO!?")
        self.sgpObject = sgp

    def setup(self):
        time.sleep(.1)
        sgp.setup()

    def shutdown(self):
        sgp.shutdown()

    def get_name(self):
        return self.name

    def get_data(self):
        return sgp.sgp.read_measurements().data[0]
