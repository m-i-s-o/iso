from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ

# @respond_to('string')     bot宛のメッセージ
#                           stringは正規表現が可能 「r'string'」
# @listen_to('string')      チャンネル内のbot宛以外の投稿
#                           @botname: では反応しないことに注意
#                           他の人へのメンションでは反応する
#                           正規表現可能
# @default_reply()          DEFAULT_REPLY と同じ働き
#                           正規表現を指定すると、他のデコーダにヒットせず、
#                           正規表現にマッチするときに反応
#                           ・・・なのだが、正規表現を指定するとエラーになる？

# message.reply('string')   @発言者名: string でメッセージを送信
# message.send('string')    string を送信
# message.react('icon_emoji')  発言者のメッセージにリアクション(スタンプ)する
#                               文字列中に':'はいらない
import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

import datetime

DEFAULT_REPLY = "HEY! I'm mibotchan."

@respond_to('ぶり')
def mention_func(message):
    message.send('<@U94JTAU9X> ブリ食べたい')

@respond_to('やっほ〜')
def mention_func(message):
    message.reply('うぇ〜い')  # メンション

@listen_to('みぼのじかん')
def mention_func(message):
    message.reply('<@U5ZUNL7J8> じかん')

@listen_to('今日も一日')
def mention_func(message):
    message.reply('がんばるぞい！')  # メンション

@listen_to('がんばる')
@listen_to('頑張る')
def mention_func(message):
    message.react('ouen')
    message.reply('がんば！')

@listen_to('ほめて')
@listen_to('褒めて')
def mention_func(message):
    message.reply('えらい！えらい！それはめちゃ偉いのでは〜〜！？:sugoi::erai:')

@listen_to('おつ〜')
@listen_to('おつかれ')
@listen_to('帰る')
def mention_func(message):
    message.reply('おつぽん！')

@listen_to('TODO')
@listen_to('ToDo')
def mention_func(message):
    message.send('がんばぇ〜')

@listen_to('みぼっちゃん')
def mention_func(message):
    message.send('いぇ〜い')

################################################################################
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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main(user_id):
    if user_id == "U4TB5L9NF":
        calendar_id = "iso@serverworks.co.jp"
    elif user_id == "U0X5AFT2A":
        calendar_id = "namai@serverworks.co.jp"
    elif user_id == "U60LFUCR1":
        return ('君はごま...！')
    else:
        return ('だれ？')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    today = datetime.date.today()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    today_end = today.isoformat() + 'T19:00:00+09:00'

    check = {
      "timeMin": now,
      "timeMax": today_end,
      "timeZone": "Asia/Tokyo",
      "groupExpansionMax": 5,
      "calendarExpansionMax": 5,
      "items": [
        {
          "id": calendar_id
        }
      ]
    }

    try:
        que = service.freebusy().query(body=check).execute()
    except Exception:
        return ('19時すぎてるよ！')
    busy_events = que["calendars"][calendar_id]["busy"]
    my_schedule = calc_mytime(busy_events, today_end)
    return my_schedule


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


def calc_mytime(busy_events, today_end):
    calc_zero = '2017-10-25T17:00:00+09:00'
    mytime = calc_delta(calc_zero, calc_zero)
    prev_end = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    next_message = ""

    if len(busy_events) == 0:
        pass
    else:
        i = 0
        for i in busy_events:
            next_start = i["start"]
            next_message += '次のよていは ' + next_start[11:16] + ' から\n'
            mytime += calc_delta(next_start, prev_end)
            prev_end = i["end"]
    mytime += calc_delta(today_end, prev_end)
    if next_message == "":
        message_body = 'のこり時間 → ' + str(mytime)[0:-3]
    else:
        message_body = 'のこり時間 → ' + str(mytime)[0:-3] + '\n ' + next_message
    return message_body

################################################################################


@respond_to('残り時間')
@respond_to('のこり')
@respond_to('じかん')
@respond_to('時間')
def usable_time(message):
    time_schedule = main(message.body["user"])
    message.send(str(time_schedule))


################################################################################
@respond_to('test')
def mention_func(message):
    message.send(str(message.body["user"]))
