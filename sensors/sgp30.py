import time
from smbus2 import SMBusWrapper
from sgp30 import Sgp30
import time

addr = 0x58

class SGP30():
    def __init__(self):
        global addr
        self.addr = addr
        self.sensor_running = False

    def get_data(self):
        return(self.sgp30.eCO2, self.sgp30.TVOC)

    def run_sensor(self):
        pass

    def setup(self):
        if not self.sensor_running:
            print("Initializing SGP30 Sensor...")
            with SMBusWrapper(1) as bus:
                self.sgp = Sgp30(bus)  # things thing with the baselinefile is dumb and will be changed in the future
                #print("resetting all i2c devices")
                self.sgp.i2c_geral_call()  # WARNING: Will reset any device on teh i2cbus that listens for general call
                # print(self.sgp.read_features())
                # print(self.sgp.read_serial())
                self.sgp.init_sgp()
                time.sleep(20)

            # i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
            # time.sleep(.5)
            # self.sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
            # time.sleep(.5)
            # self.sgp30.iaq_init()
            # time.sleep(10)
            self.raw = self.sgp.read_measurements().data
            self.co2 = self.sgp.read_measurements().data[0]
            self.tvoc = self.sgp.read_measurements().data[1]
            print("Sensor Started")

SGPsensor = SGP30()

if __name__ == "__main__":
    SGPsensor.setup()
    while True:
        print(SGPsensor.tvoc)
        print(SGPsensor.co2)
        print(SGPsensor.raw)
        print(SGPsensor.sgp.read_measurements())
        time.sleep(1)