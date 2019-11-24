import time

from sensors import sgp30_sensor
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
        self.sensor_running = False

    def setup(self):
        try:
            time.sleep(.1)
            sgp.setup()
            if sgp.sensor_running:
                self.sensor_running = True
        except Exception as err:
            logger.warning("Error starting %s: %s" % (self.name, err))

    def shutdown(self):
        sgp.shutdown()

    def get_name(self):
        return self.name

    def get_data(self):
        return sgp.sgp.read_measurements().data[0]
