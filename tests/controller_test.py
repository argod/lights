
import numpy as np
from lights.lights import LightsController
import time


def main():

    controller = LightsController(red_pin=22, green_pin=17, blue_pin=24)

    colors = np.array([[255, 220, 184],
    [255, 228, 189],
    [255, 236, 195],
    [255, 244, 200],
    [253, 229, 183],
    [250, 214, 165],
    [253, 94, 83],
    [120, 99, 97],
    [72, 61, 76],
    [118, 94, 134],
    [209, 178, 167]])

    for index in range(colors.shape[0]):
        color = colors[index, :]
        controller.change_to_color(color)
        time.sleep(2)

if __name__ == '__main__':
    main()