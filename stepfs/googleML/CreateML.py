import configparser
import requests
from requests_oauthlib import OAuth2Session

config = configparser.ConfigParser()
config.read("config.ini")

client_id = config["Google"]["CLIENT_ID"]
client_secret = config["Google"]["CLIENT_SECRET"]
redirect_uri = config["Google"]["REDIRECT_URI"]
authorization_base_url = config["Google"]["AUTHORIZATION_BASE_URL"]
token_url = config["Google"]["TOKEN_URL"]

# 送られてくるパラメータ：[ML名、MLのアドレス、説明、アドレスリスト、pid、node番号]
"""
# テスト用
ml_address = "mail_list@serverworks"
ml_name = "name"
ml_descr = "こういうものです"
address_list = ["a", "b", "c"]
process_instance_id = "000"
node_number = "111"
"""

QUE_URL = config["Questetra"]["URL"]


def create_ml(event, context):
    # パラメータを作成
    param = {}
    response = {"Google_res": "", "error_res": ""}

    param["email"] = event["ml_address"]
    param["name"] = event["ml_name"]
    if ml_descr is not None:
        param["description"] = event["ml_descr"]
    else:
        param["description"] = ''

    address_list = event["address_list"]
    # アドレスリストが空だったらそちらへ分岐。→＆分岐条件にhttp-req
    if address_list is None:
        response["error_res"] = 'MLに追加するメールアドレスが指定されていません。'
    # リストの要素の数だけループ
    else:
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
        for i in address_list:
            # GoogleのアドレスにPOSTしてML作成
            create_url = config["Google"]["GROUP_URL"]

            google_res = google.post(
                google_url,
                data=param
            )
            print(google_res)

            response["Google_res"] = google_res
            # エラーが出たら終了。
            if google_res["error(てきとう)"] is not None:
                response["error_res"] = google_res["error(てきとう)"]
            else:
                pass
    return response
