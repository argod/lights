import schedule
import time
import pigpio
import logging

from lights.lights import LightsController
from lights.motion import MotionController
from lights.overlay.constructor import create_overlay
from lights.schedule import LightScheduler

lights_logger = logging.getLogger("lights")
motion_logger = logging.getLogger("motion")
controller_logger = logging.getLogger("controller")


class Controller:

    def __init__(self, config):

        pi = pigpio.pi()

        self.do_stop = False
        controller_config = config['controller']
        led_count = controller_config['led_count']

        self.motion_detection_interval = controller_config['motion_detection_interval']
        self.max_idle = controller_config['maximum_number_of_idle']

        self.lights_refresh_rate = controller_config['lights_refresh_rate']

        self.lights_controller = LightsController(config['lights'], led_count=led_count)
        self.light_schedule = LightScheduler(controller_config['schedule_path'],  led_count=led_count)
        self.motion_controller = MotionController(pi, controller_config['motion_pin'])

        self.on = True
        self.idle_count = 0
        self.overlays = []

        for overlay in config['overlays']:
            overlay_name = overlay['name']
            overlay_location = (overlay['start_led'], overlay['end_led'])
            overlay_object = create_overlay(overlay_name, overlay['configuration'], self)
            self.overlays.append((overlay_location, overlay_object))

    def _init_state(self):
        self.on = True
        self.do_stop = False
        self.idle_count = 0
        self.registered_alarms = []

    def _change_lights(self):
        if self.on:
            lights_logger.info("Changing color")
            led_colors = self.light_schedule.get_color()

            for segment, overlay in self.overlays:
                led_segment = led_colors[segment[0]:segment[1], :]
                colors_segment = overlay.get_colors(led_segment)
                led_colors[segment[0]:segment[1], :] = colors_segment

            self.lights_controller.change_to_color(led_colors)

    def _check_movement(self):
        if self.motion_controller.detect_motion():
            motion_logger.info("Motion detected")
            self.idle_count = 0
            if not self.on:
                # turn on
                self.on = True
                self._change_lights()
        else:
            self.idle_count = self.idle_count + 1
            motion_logger.info(f"No motion detected (idle count at {self.idle_count})")
            if self.idle_count == self.max_idle:
                motion_logger.info(f"Max idle exceeded ({self.max_idle}) turning off leds.")
                self.turn_off()

    def turn_off(self):
        self.on = False
        self.lights_controller.off()

    def stop(self):
        self.turn_off()
        schedule.clear()
        self.do_stop = True
        self.set_pomodoro(False)

    def _run_alarm(self):
        controller_logger.info(f"Alarm time!")
        self.lights_controller.alarm()
        return schedule.CancelJob

    def run_alarm(self, overlay_name, color):
        controller_logger.info(f"Alarm time!")
        for segment, overlay in self.overlays:
            if overlay.name == overlay_name:
                self.lights_controller.alarm(segment=segment, color=color)
        return schedule.CancelJob

    def add_alarm(self, start):
        alarm_time = start
        scheduled_time = alarm_time.strftime('%H:%M:%S')
        controller_logger.info(f"Adding alarm at {scheduled_time}")
        schedule.every().day.at(scheduled_time).do(self._run_alarm)

    def set_pomodoro(self, new_status):

        for segment, overlay in self.overlays:
            if overlay.name == 'Pomodoro':
                if new_status:
                    overlay.start()
                else:
                    overlay.stop()
        self._change_lights()

    def update_calendar_token(self, token: dict):
        for segment, overlay in self.overlays:
            if overlay.name == 'Calendar':
                overlay.update_calendar_token(token)

    def set_calendar_updates(self, status: bool):
        for segment, overlay in self.overlays:
            if overlay.name == 'Calendar':
                overlay.refresh = status

    def start(self):
        # init
        controller_logger.info("Starting process")
        self._init_state()

        self.lights_controller.alarm()
        self._change_lights()

        schedule.every(self.lights_refresh_rate).minutes.do(self._change_lights).tag("lights")
        schedule.every(self.motion_detection_interval).seconds.do(self._check_movement)

        for _, overlay in self.overlays:
            overlay.register_events()

        while True:
            try:
                schedule.run_pending()
                time.sleep(min(self.lights_refresh_rate*60, self.motion_detection_interval))
                if self.do_stop:
                    return
            except Exception as e:
                controller_logger.error(f"Non recoverable error: {e}")
                self.stop()
