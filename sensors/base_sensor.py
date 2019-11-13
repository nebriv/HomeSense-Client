import uuid

addr = None

class Sensor(object):
    def __init__(self):
        self.name = "Not Implemented"
        self.generate_id()

    def setup(self):
        return NotImplemented

    def get_name(self):
        return self.name

    def shutdown(self):
        pass

    def get_data(self):
        return NotImplementedError

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def __eq(self, other):
        return self.name == other.name

def main():
    sensor = Sensor()


if __name__ == "__main__":
    main()