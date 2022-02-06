import pigpio
import time

SLEEP_TIME = 0.5
NUMBER_ITERATIONS = 10
MOTION_COUNT = 3


class MotionController:

    def __init__(self, pi, pin):
        self.pi = pi
        self.pin = pin
        pi.set_mode(self.pin, pigpio.INPUT)

    def detect_motion(self):
        count = 0
        for _ in range(NUMBER_ITERATIONS):
            i = self.pi.read(self.pin)
            if i == 0:  # When output from motion sensor is LOW
                count = 0
            elif i == 1:  # When output from motion sensor is HIGH
                count = count + 1
                if count == MOTION_COUNT:
                    return True
            time.sleep(SLEEP_TIME)
        return False
