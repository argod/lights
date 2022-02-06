
import numpy as np
import time
from rpi_ws281x import *


def _create_color(value: np.ndarray):
    final_color = np.zeros(3, dtype=np.int)
    for i in range(3):
        current_value = int(value[i])
        if current_value > 255:
            current_value = 255
        elif current_value < 0:
            current_value = 0
        final_color[i] = current_value
    return final_color


class LightsController:

    def __init__(self, config, led_count: int):

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(led_count,
                                       config['pin'],
                                       config['led_frequency_hz'],
                                       config['led_dma'],
                                       config['led_invert'],
                                       config['led_brightness'],
                                       config['led_channel'],
                                       ws.WS2812_STRIP)
        # Initialize the library (must be called once before other functions).
        self.strip.begin()
        self.led_count = led_count
        self.current_colors = np.zeros((led_count, 3), dtype=np.int)
        self.change_to_color(self.current_colors)

    def change_to_color(self, colors: np.ndarray):

        for led_index in range(self.led_count):
            current_color = _create_color(colors[led_index, :])
            if not (current_color == self.current_colors[led_index, :]).all():
                color = Color(int(current_color[0]), int(current_color[1]), int(current_color[2]))
                self.strip.setPixelColor(led_index, color)
                self.current_colors[led_index, :] = current_color
        self.strip.show()

    def alarm(self, segment=None, color=np.array([255, 0, 0]), wait_ms=100, iterations=10):
        color = Color(int(color[0]), int(color[1]), int(color[2]))
        start, stop = 0, self.led_count
        if segment:
            start, stop = segment
        for j in range(iterations):
            for q in range(3):
                for i in range(start, stop, 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(start, stop, 3):
                    self.strip.setPixelColor(i + q, 0)

        # restore
        for led_index in range(self.led_count):
            current_color = _create_color(self.current_colors[led_index, :])
            color = Color(int(current_color[0]), int(current_color[1]), int(current_color[2]))
            self.strip.setPixelColor(led_index, color)
        self.strip.show()

    def off(self):
        self.change_to_color(np.zeros((self.led_count, 3), dtype=np.int))
