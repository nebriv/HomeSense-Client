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
        global HTU21DF
        Sensor.__init__(self)
        self.htuObject = HTU21DF
        print(self.htuObject.dummy_var)
        self.name = "Humidity"
        self.unit = "fahrenheit"

    def get_name(self):
        return self.name

    def get_data(self):
        return self.htuObject.humidity

    def setup(self):
        time.sleep(.1)
        if not self.htuObject.sensor_running:
            self.htuObject.setup()