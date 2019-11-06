from tsl2561 import TSL2561
from time import sleep
import pigpio
from .base_sensor import Sensor

class Lux(Sensor):

    def __init__(self):
        super(Sensor, self).__init__()
        self.name = "light"
        self.tsl = TSL2561(debug=1)
        self.tsl.set_auto_range(16)

    def get_data(self):
        #return 54
        return self.tsl.lux()

    def get_name(self):
        return self.name