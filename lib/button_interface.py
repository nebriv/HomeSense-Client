import RPi.GPIO as GPIO
import time
from . import display
from . import device_manage
import subprocess
import logging

logger = logging.getLogger(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

reset_wifi = 5
reset_device = 15

class UI:
    def __init__(self, halt):
        self.counter = 0
        self.display = display.screen
        self.halt = halt

    def wait_for_press(self):
        print("In loop")
        while True:

            #self.display.update_screen(["Waiting for button press"])
            while GPIO.input(17) == 1:
                self.display.display_blocker("Button Interface")
                if self.counter == 0:
                    self.display.update_screen(["Device Reset Menu Triggered"], "Button Interface")
                    time.sleep(2)

                self.display.update_screen(["5 = Wifi", "15 = Device", "%s seconds" % self.counter], "Button Interface")
                self.display.update_screen(["Test"])
                time.sleep(1)
                self.counter += 1
                if self.halt:
                    self.display.remove_blocker()
                    break
            if reset_device > self.counter > reset_wifi:
                self.display.remove_blocker()
                self.reset_wifi()
            elif self.counter > reset_device:
                self.reset_device()
            self.counter = 0
            self.display.remove_blocker()
            if self.halt:
                self.display.remove_blocker()
                break

    def reset_wifi(self):
        self.display.update_screen(["Reset Wifi?", "Press and hold to continue..."], "Button Interface")
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if GPIO.input(17) == 1:
                self.display.update_screen(["Reseting Wifi"], "Button Interface")
                time.sleep(2)
                self.display.remove_blocker()
                self.display.clear()
                command = "sudo python3 -m lib.device_manage --host"
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                while True:
                    line = p.stdout.readline().decode("utf-8")
                    logger.debug(line)
                    if not line: break
                break
            if counter > 10:
                self.display.update_screen(["Reset Wifi timed out."], "Button Interface")
                self.display.remove_blocker()
                self.display.clear()
                break

    def reset_device(self):
        self.display.update_screen(["Reset Device?", "Press and hold to continue..."], "Button Interface")
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if GPIO.input(17) == 1:
                self.display.update_screen(["Reseting Device"], "Button Interface")
                time.sleep(2)
                self.display.remove_blocker()
                self.display.clear()
                command = "sudo python3 -m lib.device_manage --device"
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                while True:
                    line = p.stdout.readline().decode("utf-8")
                    logger.debug(line)
                    if not line: break
                break
            if counter > 10:
                self.display.update_screen(["Reset Device timed out."], "Button Interface")
                self.display.remove_blocker()
                self.display.clear()
                break

if __name__ == "__main__":
    halt = False
    try:
        bm = UI(halt)
        bm.wait_for_press()
    except KeyboardInterrupt:
        halt = True


