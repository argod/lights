import datetime
import numpy as np
import schedule
import logging
from enum import Enum

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

logger = logging.getLogger("pomodoro")

class State(Enum):
    WORKING = 0
    SHORT_BREAK = 1
    LONG_BREAK = 2

class Pomodoro:

    def __init__(self, config, controller):

        self.name = 'Pomodoro'

        working_color = np.array([int(x) for x in config['working_color'].split(',')])
        short_pause_color = np.array([int(x) for x in config['short_pause_color'].split(',')])
        long_pause_color = np.array([int(x) for x in config['long_pause_color'].split(',')])

        working_time = config['working_time']
        short_pause_time = config['short_pause_time']
        long_pause_time = config['long_pause_time']

        self.map = {
            State.WORKING: (working_color, working_time),
            State.SHORT_BREAK: (short_pause_color, short_pause_time),
            State.LONG_BREAK: (long_pause_color, long_pause_time),
        }
        self.dim_factor = config['dim_factor']
        self.work_blocks = config['work_blocks']

        self.started = False
        self.current_blocks = 0
        self.current_state_start = None
        self.current_state = State.WORKING
        self.controller = controller

    def start(self):
        logger.info("starting pomodoro")
        self.started = True
        self.current_blocks = 0
        self._configure_state(State.WORKING)

    def stop(self):
        logger.info("ending pomodoro")
        self.started = False
        schedule.clear('pomodoro')

    def _change_state(self):


        if not self.started:
            return schedule.CancelJob
        if self.current_state == State.WORKING:
            self.current_blocks += 1
            if self.current_blocks == self.work_blocks:
                self._configure_state(State.LONG_BREAK)
            else:
                self._configure_state(State.SHORT_BREAK)
        elif self.current_state == State.LONG_BREAK:
            self.current_blocks = 0
            self._configure_state(State.WORKING)
        elif self.current_state == State.SHORT_BREAK:
            self._configure_state(State.WORKING)
        return schedule.CancelJob

    def _configure_state(self, new_state):
        logger.info(f"changing status from {self.current_state} to {new_state}")
        now = datetime.datetime.now()
        now = now.replace(tzinfo=LOCAL_TIMEZONE)

        self.current_state = new_state
        self.current_state_start = now
        new_state_color, wait_time = self.map[new_state]
        alarm_time = now + datetime.timedelta(minutes=wait_time)
        scheduled_time = alarm_time.strftime('%H:%M:%S')
        self.controller.run_alarm(self.name, new_state_color)
        schedule.every().day.at(scheduled_time).do(self._change_state).tag("pomodoro")

    def get_colors(self, background: np.ndarray):
        if not self.started:
            return background
        else:
            background = self.dim_factor*background
            color, wait_time = self.map[self.current_state]
            now = datetime.datetime.now()
            now = now.replace(tzinfo=LOCAL_TIMEZONE)

            state_end = self.current_state_start + datetime.timedelta(minutes=wait_time)

            total_duration = (state_end - self.current_state_start).total_seconds()
            duration = (now - self.current_state_start).total_seconds()
            proportion = duration/total_duration

            led_length = background.shape[0]
            pixels_to_change = int(led_length * proportion)
            if pixels_to_change > 0:
                color_block = np.repeat(np.expand_dims(color, axis=0), pixels_to_change, axis=0)
                background[0:pixels_to_change, :] = color_block
            return background

    def register_events(self):
        pass

