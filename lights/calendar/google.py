import logging
import os.path
import datetime
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarAPI:

    def __init__(self, token_path, credentials_path):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.credentials = None

    def get_credentials(self):

        if not self.credentials:

            if os.path.exists(self.token_path):
                self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            if not self.credentials or not self.credentials.valid:
                return None

        return self.credentials

    def update_calendar_token(self, token: dict):
        self.credentials = Credentials.from_authorized_user_info(token, SCOPES)
        # save it
        json_object = json.dumps(token)
        with open(self.token_path, 'w') as token:
            token.write(json_object)

    def get_events(self, start_datetime, end_datetime):
        """Shows basic usage of the Google Calendar API.
            Prints the start and name of the next 10 events on the user's calendar.
            """
        creds = self.get_credentials()
        if not creds:
            logger.error("Could not retrieve credentials")
            return []
        try:
            service = build('calendar', 'v3', credentials=creds)

            events_result = service.events().list(calendarId='primary', timeMin=start_datetime.isoformat(),
                                                  timeMax=end_datetime.isoformat(),
                                                  singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                logger.info('No upcoming events found.')
                return []

            events_results = []

            for event in events:
                summary = ""
                if 'summary' in event and event['summary']:
                    summary = event['summary']

                if summary.find("(via Clockwise)") <= 0:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['start'].get('date'))
                    try:
                        start_datetime = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
                        end_datetime = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')

                        events_results.append((start_datetime, end_datetime))
                    except ValueError as e:
                        logger.warning(f"Error processing event {event['summary']}. value error {e}")
                else:
                    logger.info(f"event {event['summary']} discarded")
            return events_results

        except HttpError as error:
            logger.error('An error occurred: %s' % error)
            return []
