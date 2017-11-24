# coding=UTF-8

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from datetime import datetime,timedelta
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'slacker'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_kintai_event():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.now() #+ 'Z'  'Z' indicates UTC time
    str_now = now.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    one_hour_later = now + datetime.timedelta(hours=1) 
    str_later = one_hour_later.strftime('%Y-%m-%dT%H:%M:%S+09:00')

    events = service.events().list(calendarId='primary', timeMin=str_now, timeMax=str_later).execute()
    display_events = ""
    byte_CWS = "クラウドワークスタイル".encode("shift_jis")
    byte_holiday = "お休み".encode("shift_jis")
    for event in events['items']:
        if 'クラウドワークスタイル' in event['summary'] or 'お休み' in event['summary']:
            display_events += (event['summary'] + ",")
    return display_events[:-1]

if __name__ == '__main__':
    kintai_events = get_kintai_event()
    print(kintai_events + 'です。')
