import datetime
import logging
import os
import pickle
import pkgutil
import sched
import signal
import subprocess
import sys
import threading
import time
import uuid
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from threading import Thread

import git
import psutil
import requests

from lib.daemon import Daemon
from lib import display
from lib import device_manage
from lib import conn_test
from lib import button_interface

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create the logging file handler
fh = RotatingFileHandler("monitor.log", maxBytes=200000000,
                              backupCount=5)
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
    run_time = 0
    start_time = None
    threads = []
    thread_halt = False
    scheduled_tasks = []
    reg_code = None

    token = None

    # Settings
    update_setting_frequency = 30
    update_frequency = 600
    display_brightness = 100
    screen_on = True
    log_level = "INFO"

    def sched_sleeper(self,time_sleep):
        if self.thread_halt:
            logging.debug("Exiting sched sleeper")
            exit()
        else:
            time.sleep(time_sleep)

    def device_clock(self):
        while True:
            if self.thread_halt:
                logging.debug("Exiting device clock")
                break
            if self.start_time is None:
                self.start_time = datetime.datetime.now()
            else:
                now = datetime.datetime.now()
                self.run_time = (now - self.start_time).total_seconds()
            time.sleep(1)

    def start_device_clock(self):
        thread1 = Thread(target=self.device_clock)
        thread1.daemon = True
        thread1.start()
        self.threads.append(thread1)
        return True

    def start_button_monitor(self):
        bm = button_interface.UI(self.thread_halt)

        thread1 = Thread(target=bm.wait_for_press)
        thread1.daemon = True
        thread1.start()
        self.threads.append(thread1)

    def add_scheduled_task(self, function, time, **args):
        logger.debug("Adding task: %s" % str(function.__name__))
        task = self.scheduler.enter(time, 1, function, (args))
        self.scheduled_tasks.append(task)

    def check_for_updates(self):
        # TODO: Need to install requirements

        try:
            self.display.update_screen(["Checking for updates"])
            logger.info("Checking for sensor updates")

            g = git.cmd.Git(os.getcwd())
            update_results = g.pull()
            if "Updating " in update_results:
                self.display.update_screen(["Update found, restarting..."])
                restart_program()
        except Exception as err:
            logger.error(err)
            #print("CAUGHT EXCEPTION DURING UPDATES: %s" % err)

        self.add_scheduled_task(self.check_for_updates, 600)

    def keyboard_interrupt(self, signal, frame):
        logger.info("Keyboard Interrupt - Shutting Down")
        self.display.update_screen(["Shutting Down!"])
        self.thread_halt = True

        logger.debug("Number of running threads: %s" % threading.active_count() )


        logger.debug("Stopping particles...")
        for particle in self.particles:
            try:
                particle.shutdown()
            except Exception as err:
                logger.warning(err)

        logger.debug("Canceling tasks...")
        try:
            for task in self.scheduled_tasks:
                self.scheduler.cancel(task)
        except Exception as err:
            logger.debug("%s" % err)

        del(self.scheduler)

        time.sleep(2)
        self.display.clear()
        logger.debug("Trying to exit...")
        logger.debug("Number of running threads: %s" % threading.active_count() )
        exit(0)

    def first_start(self):
        if os.path.isfile("sensor.dat"):
            return False
        else:
            return True

    def generate_device_id(self):
        self.device_id = str(uuid.uuid4())

    def set_logging_level(self, level):
        levels = {'CRITICAL': logging.critical,
                  'ERROR': logging.error,
                  'WARNING': logging.warning,
                  'INFO': logging.info,
                  'DEBUG': logging.debug
                  }
        try:
            logger.info("Changing log level to: %s" % level)
            logger.setLevel(levels[level])
        except Exception as err:
            logger.setLevel(levels['INFO'])
            logger.warning("Invalid logging level (%s) from server settings" % level)

    def reload_settings(self):
        self.display.set_brightness(self.display_brightness)
        self.display.screen_onoff(self.screen_on)
        self.set_logging_level(self.log_level)

    def get_settings(self):
        settings_updated = False
        try:
            logger.debug("Getting sensor settings from cloud")
            #self.display.update_screen(["Getting Sensor Settings"])
            data = {'device_id': self.device_id, 'token': self.token}

            r = requests.get(self.api_server + "/api/sensors/sensor_settings/", params=data)

            new_settings = r.json()
            if "update_frequency" in new_settings:
                if new_settings['update_frequency'] != self.update_frequency:
                    logger.debug("Update frequency changed to: %s" % new_settings['update_frequency'])
                    self.update_frequency = new_settings['update_frequency']
                    settings_updated = True

            if "display_brightness" in new_settings:
                if new_settings['display_brightness'] != self.display_brightness:
                    logger.debug("Display brightness changed to: %s" % new_settings['display_brightness'])
                    self.display_brightness = new_settings['display_brightness']
                    settings_updated = True

            if "screen_on" in new_settings:
                if new_settings['screen_on'] != self.screen_on:
                    logger.debug("Screen On changed to: %s" % new_settings['screen_on'])
                    self.screen_on = new_settings['screen_on']
                    settings_updated = True

            if "update_setting_frequency" in new_settings:
                if new_settings['update_setting_frequency'] != self.update_setting_frequency:
                    logger.debug("Update Setting Frequency changed to: %s" % new_settings['update_setting_frequency'])
                    self.update_setting_frequency = new_settings['update_setting_frequency']
                    settings_updated = True

            if "log_level" in new_settings:
                if new_settings['log_level'] != self.log_level:
                    logger.debug("Log level changed to: %s" % new_settings['log_level'])
                    self.log_level = new_settings['log_level']
                    settings_updated = True

            if settings_updated:
                self.reload_settings()

        except Exception as err:
            logger.error("Error getting sensor settings from cloud: %s" % err)

        self.add_scheduled_task(self.get_settings, self.update_setting_frequency)

    def wait_for_registration(self, retry=0):
        if self.reg_code:
            logger.info("Waiting for registration")
            self.display.update_screen(["Registration Code:", self.reg_code])
            data = {'device_id': self.device_id, 'token': self.token}
            r = requests.post(self.api_server + "/api/sensors/check_registration/", data=data)
            if r.status_code < 400:
                logger.info("Registration success")
                self.display.update_screen(["Welcome to HomeSense!"])
                time.sleep(15)
                return True
            else:
                if retry > 120:
                    self.display.update_screen(["Registration Timeout...", "=( Reboot to try again"])
                    time.sleep(120)
                    return True
                if retry > 60:
                    time.sleep(15)
                else:
                    time.sleep(5)
                retry += 1
                self.wait_for_registration()

    def register_particles(self):
        data = {"device_id": self.device_id, "token": self.token}
        r = requests.get(self.api_server + "/api/sensors/sensor_particles/", params=data)
        registered_particles = r.json()['particle_names']

        try:
            for each in self.particles:
                if each.name not in registered_particles:
                    data = {"device_id": self.device_id,
                            "token": self.token,
                            "particle_name": each.name,
                            "particle_id": each.id,
                            "particle_unit": each.unit}
                    logger.debug("Uploading particle: %s" % data)

                    r = requests.post(self.api_server + "/api/sensors/add_particle/", data=data)

                    if r.status_code == 201:
                        logger.info("Successfully Registered Particle %s" % data['particle_name'])
                    else:
                        logger.error("Unable to register particle with server: %s %s" % (r.status_code, r.text))
                        exit()
        except Exception as err:
            logger.error("An error occured when registering a particle: %s" % (err))
            exit()

    def register(self):
        if self.homesense_enabled:
            logger.info("Registering with HomeSense server: %s" % self.api_server)
            self.display.update_screen(["Registering with server:", self.api_server])

            data = {'device_id': self.device_id}
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
                    if "registration_code" in r.json():
                        self.reg_code = r.json()['registration_code']
                    else:
                        logger.error("No registration code received by server: %s %s" % (r.status_code, r.text))
                        exit()
                else:
                    logger.error("Unable to register with server: %s %s" % (r.status_code, r.text))
                    exit()
            except Exception as err:
                logger.error("Unable to register with server: %s" % (err))
                exit()
            self.register_particles()
            self.wait_for_registration()

    def get_i2c_addresses(self):
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

        return self.sensor_addresses

    def get_particle_by_name(self, name):
        for particle in self.particles:
            if particle.name == name:
                return particle
        return False

    def get_sensors(self):
        logger.info("Loading available particles...")
        #loaded_particle_modules = load_all_modules_from_dir("particles")
        new_sensor = False
        logger.info("Detecting sensors")
        self.display.update_screen(["Detecting Sensors..."])
        time.sleep(1)
        self.get_i2c_addresses()

        for particle_mod in self.loaded_particle_modules:
            if hex(particle_mod.addr) in self.sensor_addresses:
                particle = particle_mod.Particle()
                if not self.get_particle_by_name(particle.name):
                    logger.info("Found new particle: %s" % particle.name)
                    self.particles.append(particle)
                    new_sensor = True

        return new_sensor

    def save_particles(self):
        pickled = []

        for each in self.particles:
            logger.debug("Saving %s State" % each.name)
            pickled.append(pickle.dumps(each))

        return pickled

    def save_sensor(self):
        data = {"device_id": self.device_id, "sensors": self.save_particles(), "token": self.token}
        with open("sensor.dat", 'wb') as outfile:
            pickle.dump(data, outfile)

    def print_loaded_particle(self):
        names = []
        for particle in self.particles:
            names.append(particle.name)
        names = ", ".join(names)
        logger.debug("Loaded Particles: %s" % names)

    def load_sensor(self):
        try:
            if os.path.isfile("sensor.dat"):
                with open('sensor.dat', 'rb') as infile:
                    data = pickle.load(infile)
                self.device_id = data['device_id']
                self.token = data['token']
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
        self.display.update_screen(["Initializing Sensors..."])
        for particle in self.particles:
            logger.info("Starting %s" % particle.name)
            particle.setup()

    def first_time_setup(self):
        logger.info("Running first time setup...")
        if conn_test.test_network_connection():
            self.generate_device_id()
            self.get_sensors()
            self.register()
            self.save_sensor()
        else:
            #self.display.update_screen(["Connect to wifi:", "HomeSense Setup"])

            # Run it as a module to escape import headaches...
            command = "sudo python3 -m lib.device_manage --host"
            subprocess.run(command.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
            #manage_raspiwifi.reset_to_host_mode()
            #time.sleep(1)
            #command = "sudo python3 lib/manage_raspiwifi.py --client"
            #subprocess.run(command.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
            #manage_raspiwifi.reset_to_client_mode()
            self.first_time_setup()

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

    def upload_homesense_data(self, data, retry=0):
        try:
            logger.debug("Uploading data...")
            r = requests.post(self.api_server + "/api/data/add/", data=data)
        except Exception as err:
            if retry > 3:
                return False
            else:
                logger.warning("Error uploading data, retrying in 5 seconds...")
                time.sleep(5)
                retry += 1
                self.upload_homesense_data(data, retry)

    def wait(self, sleeptime=120):
        logger.info("Sleeping for %s seconds..." % sleeptime)
        while sleeptime > 0:
            if self.thread_halt:
                break
            self.display.update_screen(["Sleeping for %s seconds..." % sleeptime])
            time.sleep(1)
            sleeptime -= 1

    def get_data(self):
        logger.info("Getting and uploading data...")
        while True:
            self.display.update_screen(["Collecting Data..."])
            for particle in self.particles:
                #print(particle.id, particle.name, particle.get_data())
                logger.debug("Getting data: %s" % particle.name)
                data = {"particle_id": particle.id, "device_id": self.device_id, "particle_data": particle.get_data(), "token": self.token}
                self.upload_homesense_data(data)
            self.wait(self.update_frequency)

    def run(self):
        #self.start_device_clock()

        self.scheduler = sched.scheduler(time.monotonic, self.sched_sleeper)
        logger.debug("Starting Run Statement")
        signal.signal(signal.SIGINT, self.keyboard_interrupt)
        self.display = display.screen
        self.display.update_screen(["Booting..."])
        self.start_button_monitor()
        time.sleep(1)
        self.check_for_updates()
        self.load_config()
        self.loaded_particle_modules = load_all_modules_from_dir("particles")
        if self.first_start():
            self.first_time_setup()
        else:
            try:
                self.load_sensor()
                if self.get_sensors():
                    self.register_particles()
                    self.save_sensor()
            except ValueError:
                self.reset_sensor()
                self.first_time_setup()

        self.get_settings()

        t = Thread(target=self.scheduler.run)
        t.daemon = True
        t.start()
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