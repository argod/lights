import pandas as pd
import numpy as np
from datetime import datetime


def _prepare_schedule(schedule: pd.DataFrame):
    schedule['Time'] = pd.to_datetime(schedule['Time'], format='%H:%M:%S').dt.hour + \
                       (pd.to_datetime(schedule['Time'], format='%H:%M:%S').dt.minute/60)
    schedule['Color'] = schedule['Color'].apply(lambda a: np.array([int(x) for x in a.split(', ')]))
    return schedule


def _find_bounds(schedule: pd.DataFrame, current_time: float):

    if len(schedule[schedule['Time'] == current_time]) > 0:
        return schedule[schedule['Time'] == current_time], schedule[schedule['Time'] == current_time]

    upper = schedule[schedule['Time'] > current_time]
    upper_limit = schedule[schedule['Time'] == schedule['Time'].min()]
    if len(upper) > 0:
        upper_limit = upper[upper['Time'] == upper['Time'].min()]

    lower = schedule[schedule['Time'] < current_time]
    lower_limit = schedule[schedule['Time'] == schedule['Time'].max()]
    if len(lower) > 0:
        lower_limit = lower[lower['Time'] == lower['Time'].max()]

    return lower_limit, upper_limit


def _find_time_proportion(lower_time, upper_time, current_time):

    if lower_time > upper_time:
        upper_time = upper_time + 24
        if current_time < lower_time:
            current_time = current_time + 24

    total_time = upper_time - lower_time
    passed = current_time - lower_time
    return passed/total_time


def _get_color(lower_color, upper_color, proportion):
    difference = upper_color - lower_color
    return lower_color + proportion*difference


class LightScheduler:

    def __init__(self, schedule_path, led_count):
        schedule = pd.read_csv(schedule_path)
        self.schedule = _prepare_schedule(schedule)
        self.led_count = led_count

    def get_color(self):

        current_time = datetime.now().hour + datetime.now().minute / 60
        lower_bound_df, upper_bound_df = _find_bounds(self.schedule, current_time)

        if lower_bound_df['Time'].values[0] == upper_bound_df['Time'].values[0]:
            return np.repeat(np.expand_dims(lower_bound_df['Color'].values[0], axis=0), self.led_count, axis=0)

        time_lower_bound = lower_bound_df['Time'].values[0]
        time_upper_bound = upper_bound_df['Time'].values[0]

        proportion = _find_time_proportion(time_lower_bound, time_upper_bound, current_time)

        color_lower_bound = lower_bound_df['Color'].values[0]
        color_upper_bound = upper_bound_df['Color'].values[0]

        color = _get_color(color_lower_bound, color_upper_bound, proportion)

        return np.repeat(np.expand_dims(color, axis=0), self.led_count, axis=0)
