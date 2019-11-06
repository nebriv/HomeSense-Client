class Sensor(object):
    def __init__(self):
        self.name = "Not Implemented"

    def get_name(self):
        return self.name

    def get_data(self):
        return NotImplementedError

def main():
    sensor = Sensor()


if __name__ == "__main__":
    main()