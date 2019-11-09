from sensors import *

class Temperature(base_sensor.Sensor):
    def __init__(self):
        global HTU21DFSensor
        super(base_sensor.Sensor, self).__init__()
        if HTU21DFSensor:
            #print("voc- it exists")
            self.sensorObject = HTU21DFSensor
        else:
            #print("voc- it doesn't exist")
            HTU21DFSensor = HTU21DF()
            self.sensorObject = HTU21DFSensor
        self.name = "temperature"
        self.unit = "fahrenheit"

    def get_name(self):
        return self.name

    def get_data(self):
        if self.unit == "celsius":
            return self.sensorObject.temperature
        elif  self.unit == "fahrenheit":
            temperature = 9.0 / 5.0 * self.sensorObject.temperature + 32
            return temperature