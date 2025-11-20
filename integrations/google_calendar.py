from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'google_credentials.json')

def add_event_to_calendar(title, description, start_time, end_time):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Africa/Cairo'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Africa/Cairo'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')
