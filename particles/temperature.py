import time

from sensors import temperature_humidity
from sensors.base_sensor import Sensor
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create the logging file handler
fh = logging.FileHandler("homesense.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add handler to logger object
logger.addHandler(fh)


addr = 0x40

class Particle(Sensor):
    def __init__(self):
        Sensor.__init__(self)
        self.name = "Temperature"
        self.unit = "fahrenheit"
        self.sensor_running = False

    def get_name(self):
        return self.name

    def shutdown(self):
        temperature_humidity.HTU21DFSensor.stop = True

    def get_data(self):
        if self.unit == "celsius":
            return temperature_humidity.HTU21DFSensor.temperature
        elif  self.unit == "fahrenheit":
            temperature = 9.0 / 5.0 * temperature_humidity.HTU21DFSensor.temperature + 32
            return temperature

    def setup(self):
        try:
            time.sleep(.1)
            if not temperature_humidity.HTU21DFSensor.sensor_running:
                temperature_humidity.HTU21DFSensor.setup()

            if temperature_humidity.HTU21DFSensor.sensor_running:
                self.sensor_running = True
        except Exception as err:
            logger.warning("Error starting %s: %s" % (self.name, err))