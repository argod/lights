
from lights.overlay.clock import Clock, Calendar
from lights.overlay.pomodoro import Pomodoro


overlay_name_mapping = {'Clock': Clock,
                        'Calendar': Calendar,
                        'Pomodoro': Pomodoro}


def create_overlay(name, config, controller):

    if name not in overlay_name_mapping:
        raise Exception(f"overlay {name} not found")
    return overlay_name_mapping[name](config, controller)
