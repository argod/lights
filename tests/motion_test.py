import pigpio
import time

pi = pigpio.pi()
pi.set_mode(23, pigpio.INPUT)

while True:
    i = pi.read(23)
    if i == 0:  # When output from motion sensor is LOW
        print("No intruders", i)
    elif i == 1:  # When output from motion sensor is HIGH
        print("Intruder detected", i)
    time.sleep(1)
