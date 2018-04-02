import configparser
import requests
from requests_oauthlib import OAuth2Session

config = configparser.ConfigParser()
config.read("config.ini")

# 送られてくるパラメータ：[MLのアドレス、アドレスリスト、pid、node番号]
ml_address = "mail_llist@serverworks"
address_list = ["a", "b", "c"]
process_instance_id = "000"
node_number = "111"

client_id = config["Google"]["CLIENT_ID"]
client_secret = config["Google"]["CLIENT_SECRET"]
redirect_uri = config["Google"]["REDIRECT_URI"]
authorization_base_url = config["Google"]["AUTHORIZATION_BASE_URL"]
token_url = config["Google"]["TOKEN_URL"]


QUE_URL = config["Questetra"]["URL"]


def add_address2ml(event, context):
    response = {"Google_res": "", "error_res": ""}
    # パラメータを作成
    ml_address = event["ml_address"]
    address_list = event["address_list"]
    scope = config["Google"]["SCOPE"]
    scope_list = scope.split(',')
    """
    # GoogleのOAuth認証
    google = OAuth2Session(client_id, scope=scope_list, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(authorization_base_url,
        access_type="offline", prompt="none")
    r = requests.get(authorization_url)
    print('authorization_url: ' + authorization_url)
    print('redirected: ' + r.url)
    redirect_response = r.url
    # トークンを取得
    google.fetch_token(token_url, client_secret=client_secret,
            authorization_response=redirect_response)
    """

    # リストの要素の数だけループ
    for i in address_list:
        # Googleのアドレスにrequests.post
        param = {}

        # Slackでテスト
        param["text"] = "email: " + i
        param["token"] = config["Slack"]["TOKEN"]
        param["channel"] = "#ext-scratch"
        slack_url = "https://slack.com/api/chat.postMessage"
        slack_res = requests.post(
            slack_url,
            param
            )
        print(slack_res)

        param["email"] = i
        param["role"] = "MEMBER"
        google_url = config["Google"]["GROUP_URL"] + ml_address + '/members'
        google_res = google.post(
            google_url,
            data=param
        )
        print(google_res)

        # エラーが出たら終了。
        if google_res["error(てきとう)"] is not None:
            response["error_res"] = '\" ' + i + ' \"をMLに追加できませんでした。 ERROR MESSAGE: ' + google_res["error(てきとう)"]
        else:
            pass


event = {"ml_address": ml_address, "address_list": address_list}
add_address2ml(event, "")
