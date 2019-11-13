from sensors.base_sensor import Sensor
from sensors import temperature_humidity
import time

addr = 0x40


class Particle(Sensor):
    def __init__(self):
        Sensor.__init__(self)
        self.name = "Humidity"
        self.unit = "rHl"

    def get_name(self):
        return self.name

    def get_data(self):
        return temperature_humidity.HTU21DFSensor.humidity

    def setup(self):
        time.sleep(.1)
        if not temperature_humidity.HTU21DFSensor.sensor_running:
            temperature_humidity.HTU21DFSensor.setup()