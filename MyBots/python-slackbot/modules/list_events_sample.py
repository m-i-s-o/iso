from __future__ import print_function
import datetime
import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = '（アプリ名）'


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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    calendar_service = discovery.build('calendar', 'v3', http=http)

    today = datetime.date.today()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    today_end = today.isoformat() + 'T19:00:00+09:00'

    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=today_end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    # print(events)
    busies = []
    for event in events:
        an_event = dict(
            summary=event["summary"],
            start=event["start"]["dateTime"],
            end=event["end"]["dateTime"]
        )
        busies.append(an_event)

    calced_mytime = calc_mytime(busies, today_end)
    return calced_mytime


def string2datetime(str_time):
    int_year = int(str_time[0:4])
    int_month = int(str_time[5:7])
    int_day = int(str_time[8:10])
    int_hour = int(str_time[11:13])
    int_min = int(str_time[14:16])
    int_sec = int(str_time[17:19])
    dt_time = datetime.datetime(int_year, int_month, int_day, int_hour, int_min, int_sec)
    return dt_time


def calc_delta(str_next_s, str_prev_e):
    int_next_s = string2datetime(str_next_s)
    int_prev_e = string2datetime(str_prev_e)
    delta = int_next_s - int_prev_e
    return delta


def calc_mytime(busies, today_end):
    zero_delta = calc_delta('2017-10-25T17:00:00+09:00', '2017-10-25T17:00:00+09:00')
    mytime = zero_delta
    prev_end = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    next_message = ""

    if len(busies) == 0:
        pass
    else:
        i = 0
        for i in busies:
            next_start = i["start"]
            next_message += '次のよていは {0} からの `{1}`\n'.format(next_start[11:16], i["summary"])
            mytime += calc_delta(next_start, prev_end)
            prev_end = i["end"]
    mytime += calc_delta(today_end, prev_end)
    if next_message == "":
        message_body = 'のこり時間 → ' + str(mytime)[0:-3]
    else:
        message_body = 'のこり時間 → ' + str(mytime)[0:-3] + '\n ' + next_message
    return message_body



if __name__ == '__main__':
    mytime_and_busies = main()
    print(mytime_and_busies)
