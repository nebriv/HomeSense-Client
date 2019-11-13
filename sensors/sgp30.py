import time
import board
import busio
import adafruit_sgp30

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
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
            time.sleep(.5)
            self.sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
            time.sleep(.5)
            self.sgp30.iaq_init()
            time.sleep(10)
            print("Sensor Started")

SGPsensor = SGP30()

if __name__ == "__main__":
    SGPsensor.setup()
    while True:
        print(SGPsensor.get_data())
        time.sleep(1)