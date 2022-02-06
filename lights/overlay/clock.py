import datetime
import numpy as np
import schedule
import logging

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

logger = logging.getLogger("calendar")


def _get_complement(color):
    return np.array([255, 255, 255]) - color


class Clock:

    def __init__(self, config, controller):

        self.name = 'Clock'
        start_date = datetime.datetime.strptime(config['start_time'], '%H:%M:%S')
        end_date = datetime.datetime.strptime(config['end_time'], '%H:%M:%S')

        self.start = start_date.hour + (start_date.minute / 60)
        self.end = end_date.hour + (end_date.minute / 60)

        self.show_border = config['show_border']
        self.event_dim_factor = config['event_dim_factor']

        self.events = set()
        self.controller = controller
        now = datetime.datetime.now()
        self.current_day = now.replace(tzinfo=LOCAL_TIMEZONE, microsecond=0, second=0, minute=0, hour=0)

    def _check_day(self):
        # check change of day
        now = datetime.datetime.now()
        now = now.replace(tzinfo=LOCAL_TIMEZONE)

        current_day = now.replace(microsecond=0, second=0, minute=0, hour=0)
        if current_day > self.current_day:
            logger.info("new day removing previous events")
            self.events = set()
            self.current_day = current_day

    def add_event(self, start_date, end_date):

        now = datetime.datetime.now()
        now = now.replace(tzinfo=LOCAL_TIMEZONE)

        start = start_date.hour + (start_date.minute / 60)
        end = end_date.hour + (end_date.minute / 60)
        event = (start, end)
        if event not in self.events:
            self.events.add((start, end))

            if now < start_date:
                alarm_time = start_date - datetime.timedelta(seconds=30)
                self.controller.add_alarm(alarm_time)
            else:
                logger.info("Skipping, outside clock hours")

    def get_colors(self, background: np.ndarray):
        self._check_day()

        now_date = datetime.datetime.now()
        now = now_date.hour + (now_date.minute / 60)

        base_color = background[0, :]

        led_length = background.shape[0]

        proportion = (now - self.start) / (self.end - self.start)

        if 0 < proportion < 1:
            # show events
            for event_start, event_end in self.events:
                proportion_start = (event_start - self.start) / (self.end - self.start)
                proportion_end = (event_end - self.start) / (self.end - self.start)

                if proportion_start > 0 and proportion_end > 0:
                    pixel_start = int(led_length * proportion_start)
                    pixel_end = int(led_length * proportion_end)
                    background[pixel_start:pixel_end, :] = self.event_dim_factor*background[pixel_start:pixel_end, :]

            # show current time
            pixel_to_change = int(led_length * proportion)
            complement_color = _get_complement(base_color)
            background[pixel_to_change, :] = complement_color

            if self.show_border:
                background[0, :] = complement_color
                background[-1, :] = complement_color

        return background

    def register_events(self):
        pass


class Calendar:

    def __init__(self, config, controller):
        self.refresh = True
        clock_config = config['clock']
        self.name = 'Calendar'
        self.start_date = datetime.datetime.strptime(clock_config['start_time'], '%H:%M:%S')
        self.end_date = datetime.datetime.strptime(clock_config['end_time'], '%H:%M:%S')
        self.calendar_refresh_rate = config['calendar_refresh_rate']

        self.clock = Clock(clock_config, controller=controller)

        token_path = config['token_path']
        credentials_path = config['credentials_path']
        # only load this package if we are using this class
        from lights.calendar.google import CalendarAPI

        self.gCalendar = CalendarAPI(token_path, credentials_path)
        self.controller = controller
        self._update_calendar()

    def register_events(self):
        schedule.every(self.calendar_refresh_rate).minutes.do(self._update_calendar).tag("calendar")

    def _update_calendar(self):

        if not self.controller.on or not self.refresh:
            return

        logger.info("Start - Update calendar")

        now = datetime.datetime.now()
        now = now.replace(tzinfo=LOCAL_TIMEZONE)

        start_datetime = now.replace(hour=self.start_date.hour, minute=self.start_date.minute,
                                     second=self.start_date.second, microsecond=0, tzinfo=LOCAL_TIMEZONE)
        end_datetime = now.replace(hour=self.end_date.hour, minute=self.end_date.minute, second=self.end_date.second,
                                   microsecond=0, tzinfo=LOCAL_TIMEZONE)
        if start_datetime < now < end_datetime:
            logger.info("Calling google")
            events = self.gCalendar.get_events(start_datetime, end_datetime)

            for event_start, event_end in events:
                self.clock.add_event(event_start, event_end)

    def get_colors(self, background):
        return self.clock.get_colors(background)

    def update_calendar_token(self, token: dict):
        self.gCalendar.update_calendar_token(token)
