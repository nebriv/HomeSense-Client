#from smbus2 import SMBusWrapper
import time

import smbus2
from sgp30 import Sgp30

addr = 0x58

class SGP30():
    def __init__(self):
        global addr
        self.addr = addr
        self.sensor_running = False
        self.co2 = 0
        self.tvoc = 0

    def get_data(self):
        return(self.sgp30.eCO2, self.sgp30.TVOC)

    def run_sensor(self):
        pass

    def shutdown(self):
        print("Stopping SGP30 Bus")
        self.bus.close()

    def setup(self):
        if not self.sensor_running:
            print("Initializing SGP30 Sensor...")
            self.bus = smbus2.SMBus(1)

            self.sgp = Sgp30(self.bus)
            self.sgp.i2c_geral_call()
            self.sgp.init_sgp()
            time.sleep(20)
            self.sensor_running = True
            self.co2 = self.sgp.read_measurements().data[0]
            self.tvoc = self.sgp.read_measurements().data[1]
            time.sleep(2)
            print("Sensor Started")

SGPsensor = SGP30()

if __name__ == "__main__":
    SGPsensor.setup()
    while True:
        print(SGPsensor.tvoc)
        print(SGPsensor.co2)
        print(SGPsensor.sgp.read_measurements())
        time.sleep(1)