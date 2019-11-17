import RPi.GPIO as GPIO
import time
from display import Display

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

reset_wifi = 5
reset_device = 15

class UI:
    def __init__(self, halt):
        self.counter = 0
        self.display = Display()
        self.halt = halt

    def wait_for_press(self):
        while True:
            self.display.update_screen(["Waiting for button press"])
            while GPIO.input(17) == 1:
                self.display.update_screen(["5 = Wifi", "15 = Device", "%s" % self.counter])
                time.sleep(1)
                self.counter += 1
                if self.halt:
                    break
            if reset_device > self.counter > reset_wifi:
                self.reset_wifi()
            elif self.counter > reset_device:
                self.reset_device()
            self.counter = 0
            if self.halt:
                break

    def reset_wifi(self):
        self.display.update_screen(["Reseting Wifi"])
        time.sleep(5)

    def reset_device(self):
        self.display.update_screen(["Reseting Device"])
        time.sleep(5)
        self.display.clear()


if __name__ == "__main__":
    halt = False
    try:
        bm = UI(halt)
        bm.wait_for_press()
    except KeyboardInterrupt:
        halt = True


