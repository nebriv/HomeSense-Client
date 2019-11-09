import uuid

addr = None

class Sensor(object):
    def __init__(self):
        print("Hello")
        self.name = "Not Implemented"
        self.generate_id()

    def setup(self):
        return NotImplemented

    def get_name(self):
        return self.name

    def get_data(self):
        return NotImplementedError

    def generate_id(self):
        print("Generating UUID")
        self.id = str(uuid.uuid4())
        print("My UUID is: %s" % self.id)

def main():
    sensor = Sensor()


if __name__ == "__main__":
    main()