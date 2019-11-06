import time
import pigpio
import math
import binascii
from struct import unpack

from threading import Thread
#from .base_sensor import Sensor

class SGP30():
    def __init__(self):
        #super(Sensor).__init__()
        self.setup()

    def run_sensor(self):
        while True:
            self.pi.i2c_write_device(self.handle, self.measureair)
            time.sleep(.2)
            count, data = self.pi.i2c_read_device(self.handle,6)
            #print(count, data)
            #self.co2 = int.from_bytes(data[0:2], byteorder='big')
            #self.voc = int.from_bytes(data[3:4], byteorder='big')
            self.co2 = int(str(data[0:2]).encode('hex'), 16)
            self.voc = int(str(data[3:4]).encode('hex'), 16)
            #print(self.co2)
            #print("Co2: %i" % self.co2)
            #print("TVOC: %i" % self.voc)
            time.sleep(.6)


    def setup(self):
        print("Initializing SGP30 Sensor...")
        self.pi = pigpio.pi()
        self.addr = 0x58
        self.co2 = 0
        self.voc = 0

        # i2c bus, if you have a Raspberry Pi Rev A, change this to 0
        self.bus = 1

        # HTU21D-F Commands
        self.init = b"\x20\x03"
        self.measureair = b"\x20\x08"
        self.getbaseline = 0x2015
        self.setbaseline = 0x201e
        self.measuretest = 0x2032
        self.getfeatureset = 0x202f
        self.measuresignals = 0x2050
        self.handle = self.pi.i2c_open(self.bus, self.addr)
        self.pi.i2c_write_device(self.handle, self.init)
        time.sleep(1)
        self.pi.i2c_write_device(self.handle, self.measureair)

        thread1 = Thread(target=self.run_sensor)
        thread1.daemon = True
        thread1.start()
        self.sensor_running = True
        time.sleep(15)
        print("Sensor Started")

SGPsensor = None

class tvoc():
    def __init__(self):
        global SGPsensor
        if SGPsensor:
            #print("voc- it exists")
            self.sgpObject = SGPsensor
        else:
            #print("voc- it doesn't exist")
            SGPsensor = SGP30()
            self.sgpObject = SGPsensor
        self.name = "tvoc"

    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgpObject.voc

class co2():
    # REALLY JANK way to share the threaded sensor bus... but it works for now
    def __init__(self):
        # Get the SGP global var (initially set to none)
        global SGPsensor
        if SGPsensor:
            #print("co2- it exists")
            self.sgpObject = SGPsensor
        else:
            #print("co2- it doesn't exist")
            # If it doesn't exist, create it.
            SGPsensor = SGP30()
            self.sgpObject = SGPsensor
        self.name = "co2"

    def get_name(self):
        return self.name

    def get_data(self):
        return self.sgpObject.co2



def main():

    sensor = co2()
    print(sensor.name)


    sensor2 = tvoc()
    #print(sensor2.get_data())
    time.sleep(5)
    for i in range(1,5):
        print(sensor.get_data())
        print(sensor2.get_data())
        time.sleep(1)


if __name__ == "__main__":
    main()
