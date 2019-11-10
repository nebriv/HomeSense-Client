import time
import requests
import subprocess
import sys
import git
from lib.daemon import Daemon
from configparser import ConfigParser
import os
import sensors

import logging
import psutil
import uuid
from lib.display import Display
import signal
import importlib
import pkgutil
import pkgutil
import sys
import sensors
import pickle
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create the logging file handler
fh = logging.FileHandler("homesense.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add handler to logger object
logger.addHandler(fh)

def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses

def load_all_modules_from_dir(dirname):
    modules = []
    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name
                        ).load_module(package_name)
            modules.append(module)
    return modules

def int_to_en(num):
    d = { 0 : 'zero', 1 : 'one', 2 : 'two', 3 : 'three', 4 : 'four', 5 : 'five',
          6 : 'six', 7 : 'seven', 8 : 'eight', 9 : 'nine', 10 : 'ten',
          11 : 'eleven', 12 : 'twelve', 13 : 'thirteen', 14 : 'fourteen',
          15 : 'fifteen', 16 : 'sixteen', 17 : 'seventeen', 18 : 'eighteen',
          19 : 'nineteen', 20 : 'twenty',
          30 : 'thirty', 40 : 'forty', 50 : 'fifty', 60 : 'sixty',
          70 : 'seventy', 80 : 'eighty', 90 : 'ninety' }
    k = 1000
    m = k * 1000
    b = m * 1000
    t = b * 1000

    assert(0 <= num)

    if (num < 20):
        return d[num]

    if (num < 100):
        if num % 10 == 0: return d[num]
        else: return d[num // 10 * 10] + '-' + d[num % 10]

    if (num < k):
        if num % 100 == 0: return d[num // 100] + ' hundred'
        else: return d[num // 100] + ' hundred and ' + int_to_en(num % 100)

    if (num < m):
        if num % k == 0: return int_to_en(num // k) + ' thousand'
        else: return int_to_en(num // k) + ' thousand, ' + int_to_en(num % k)

    if (num < b):
        if (num % m) == 0: return int_to_en(num // m) + ' million'
        else: return int_to_en(num // m) + ' million, ' + int_to_en(num % m)

    if (num < t):
        if (num % b) == 0: return int_to_en(num // b) + ' billion'
        else: return int_to_en(num // b) + ' billion, ' + int_to_en(num % b)

    if (num % t == 0): return int_to_en(num // t) + ' trillion'
    else: return int_to_en(num // t) + ' trillion, ' + int_to_en(num % t)

    raise AssertionError('num is too large: %s' % str(num))

def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    logger.info("Restarting to apply updates")
    #print("Restarting to apply updates")
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logger.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


class Monitor(Daemon):
    particles = []
    device_id = None
    sensor_addresses = []


    def check_for_updates(self):
        try:
            self.display.update_screen(["Checking for updates"])
            logger.info("Checking for sensor updates")
            #print("Checking for sensor_updates")
            g = git.cmd.Git(os.getcwd())
            update_results = g.pull()
            if "Updating " in update_results:
                restart_program()
        except Exception as err:
            logger.error(err)
            #print("CAUGHT EXCEPTION DURING UPDATES: %s" % err)

    def keyboard_interrupt(self, signal, frame):
        logger.info("Keyboard Interrupt - Shutting Down")
        self.display.update_screen(["Shutting Down!"])
        time.sleep(5)
        self.display.clear()
        sys.exit(0)

    def first_start(self):
        if os.path.isfile("sensor.dat"):
            return False
        else:
            return True

    def generate_device_id(self):
        self.device_id = str(uuid.uuid4())

    def register(self):
        if self.homesense_enabled:
            logger.info("Registering with HomeSense server: %s" % self.api_server)
            self.display.update_screen(["Registering with server:", self.api_server])

            data = {'device_id': self.device_id}
            i = 1
            r = requests.get(self.api_server + "/api/sensors/get_token/")

            if r.status_code == 200:
                logger.info("Received sensor token from server")
                self.token = r.json()['token']
            else:
                #print(r.status_code, r.text)
                logger.error("Unable to get token from server: %s %s" % (r.status_code, r.text))
                exit()
            try:

                data['token'] = self.token

                r = requests.post(self.api_server + "/api/sensors/register/", data=data)
                if r.status_code == 201:
                    logger.info("Successfully Registered Sensor")
                else:
                    #print(r.status_code, r.text)
                    logger.error("Unable to register with server: %s %s" % (r.status_code, r.text))
                    exit()
            except Exception as err:
                logger.error("Unable to register with server: %s" % (err))
                exit()

            try:
                for each in self.particles:
                    data = {"device_id": self.device_id,
                            "particle_name": each.name,
                            "particle_id": each.id,
                            "particle_unit": each.unit}
                    logger.debug("Uploading particle: %s" % data)

                    r = requests.post(self.api_server + "/api/sensors/add_particle/", data=data)

                    print(r.status_code)
                    print(r.text)

                    if r.status_code == 201:
                        print("OK")
                        logger.info("Successfully Registered Particle %s" % each['name'])
                    else:
                        print("WTF")
                        #print(r.status_code, r.text)
                        logger.error("Unable to register particle with server: %s %s" % (r.status_code, r.text))
                        exit()
            except Exception as err:
                logger.error("Except caught?: %s" % (err))
                exit()

    def get_sensors(self):
        logger.info("Loading available particles...")
        loaded_particle_modules = load_all_modules_from_dir("particles")

        logger.info("Detecting sensors")
        self.display.update_screen(["Detecting Sensors..."])
        time.sleep(1)

        try:
            p = subprocess.Popen(['i2cdetect', '-y', '1'], stdout=subprocess.PIPE, )
            firstLine = True
            self.sensor_addresses = []

            for i in range(1, 9):
                if firstLine:
                    line = str(p.stdout.readline()).strip()
                    firstLine = False
                else:
                    line = str(p.stdout.readline()).strip()
                    # print line
                    entry = line.split(" ")
                    entry = entry[1:]
                    for each in entry:
                        if (each != "") and (each != "--"):
                            # print(each)
                            self.sensor_addresses.append("0x%s" % each)
        except Exception as err:
            logger.warning("i2cdetect not supported, setting dummy vars")
            #print("Not supported on this OS, setting dummy vars")
            self.sensor_addresses = ['0x40', '0x60', '0x39']

        logger.debug("Found sensor addresses: %s" % " ".join(self.sensor_addresses))
        self.particles = []
        for particle_mod in loaded_particle_modules:
            if hex(particle_mod.addr) in self.sensor_addresses:
                particle = particle_mod.Particle()
                logger.info("Found particle: %s" % particle.name)
                self.particles.append(particle)

        self.save_particles()

    def save_particles(self):
        pickled = []
        for each in self.particles:
            logger.debug("Saving %s State" % each.name)
            pickled.append(pickle.dumps(each))

        return pickled

    def save_sensor(self):
        data = {"device_id": self.device_id, "sensors": self.save_particles()}
        with open("sensor.dat", 'wb') as outfile:
            pickle.dump(data, outfile)

    def print_loaded_particle(self):
        names = []
        for particle in self.particles:
            names.append(particle.name)
        names = ", ".join(names)
        logger.info("Loaded Particles: %s" % names)

    def load_sensor(self):
        try:
            if os.path.isfile("sensor.dat"):
                with open('sensor.dat', 'r') as infile:
                    data = pickle.load(infile)
                self.device_id = data['device_id']
                for each in data['sensors']:
                    self.particles.append(pickle.loads(each))
                logger.debug("Loaded sensor data. Device ID: %s" % self.device_id)
                self.print_loaded_particle()
            else:
                raise FileNotFoundError("Sensor Data not found.")
        except Exception as err:
            logger.error("Error loading sensor config: %s" % err)
            raise ValueError("Error loading sensor config: %s" % err)

    def initialize_sensors(self):
        logger.info("Initializing Sensors...")
        for particle in self.particles:
            logger.info("Starting %s" % particle.name)
            particle.setup()

    def first_time_setup(self):
        logger.info("Running first time setup...")
        self.generate_device_id()
        self.get_sensors()
        self.register()
        self.save_sensor()

    def load_config(self):
        self.config = ConfigParser()
        try:
            logger.info("Trying to read homesense.conf")
            with open('homesense.conf') as f:
                self.config.read_file(f)
                if self.config.has_section("HomeSense"):
                    self.homesense_enabled = True
                    self.api_server = self.config.get('HomeSense', 'server')
                    if self.config.has_option('HomeSense', 'dev_server'):
                        self.api_server = self.config.get('HomeSense', 'dev_server')
                    if self.config.has_option('HomeSense', 'noServer'):
                        self.noServer = self.config.get('HomeSense', 'noServer')
                    else:
                        self.noServer = False

        except IOError as err:
            logger.warning("Config file not found")
            print("Config File Not Found.")
            exit()

    def reset_sensor(self):
        logger.info("Reseting Sensor")
        os.remove('sensor.dat')

    def upload_homesense_data(self, data):
        logger.info("Uploading data...")
        r = requests.post(self.api_server + "/api/data/add/", data=data)
        print(r.text)

    def get_data(self):
        while True:
            for particle in self.particles:
                print(particle.id, particle.name, particle.get_data())
                data = {"particle_id": particle.id, "device_id": self.device_id, "sensor_data": particle.get_data(), "token": self.token}
                self.upload_homesense_data(data)
            time.sleep(5)

    def run(self):
        logger.debug("Starting Run Statement")
        signal.signal(signal.SIGINT, self.keyboard_interrupt)
        self.display = Display()
        #self.display.dim()
        self.display.update_screen(["Booting..."])
        time.sleep(1)
        self.check_for_updates()
        self.load_config()
        self.loaded_particle_modules = load_all_modules_from_dir("particles")
        if self.first_start():
            self.first_time_setup()
        else:
            try:
                self.load_sensor()
            except ValueError:
                self.reset_sensor()
                self.first_time_setup()

        self.initialize_sensors()
        self.get_data()

if __name__ == "__main__":
    daemon = Monitor('homesense.pid', verbose=2)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'debug' == sys.argv[1]:

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            daemon.run()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)