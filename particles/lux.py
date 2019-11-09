from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor

addr = 0x39

class Particle(Sensor):

    def __init__(self):
        Sensor.__init__(self)
        self.name = "Light"
        self.unit = "lux"
        self.tsl = TSL2561(debug=1)
        self.tsl.set_auto_range(16)

    def get_data(self):
        #return 54
        return self.tsl.lux()

    def get_name(self):
        return self.name

    def setup(self):
        print("Nothing to setup")
        return True