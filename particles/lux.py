from tsl2561 import TSL2561

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


addr = 0x39

class Particle(Sensor):

    def __init__(self):
        Sensor.__init__(self)
        self.name = "Light"
        self.unit = "lux"

    def get_data(self):
        #return 54
        return self.tsl.lux()

    def get_name(self):
        return self.name

    def setup(self):
        try:
            self.tsl = TSL2561(debug=1)
            self.tsl.set_auto_range(16)
            self.sensor_running = True
        except Exception as err:
            logger.warning("Error starting %s: %s" % (self.name, err))