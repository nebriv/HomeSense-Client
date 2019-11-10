import sched
import time
import threading

def hi():
    print("hi")

scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(10, 1, hi, ())

print("Starting...")



time.sleep(30)
print("Done")