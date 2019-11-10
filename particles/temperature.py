from tsl2561 import TSL2561
from time import sleep
import pigpio
from sensors.base_sensor import Sensor
from sensors import temperature_humidity
import time

addr = 0x40
HTU21DF = temperature_humidity.HTU21DFSensor

class Particle(Sensor):
    def __init__(self):
        Sensor.__init__(self)
        global HTU21DF
        self.htuObject = HTU21DF
        self.name = "Temperature"
        self.unit = "fahrenheit"

    def get_name(self):
        return self.name

    def get_data(self):
        if self.unit == "celsius":
            return self.htuObject.temperature
        elif  self.unit == "fahrenheit":
            temperature = 9.0 / 5.0 * self.htuObject.temperature + 32
            return temperature

    def setup(self):
        time.sleep(.1)
        if not self.htuObject.sensor_running:
            self.htuObject.setup()