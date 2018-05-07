# -*- coding: utf-8 -*-
import configparser
import json
import logging
import requests
from time import sleep

config = configparser.ConfigParser()
config.read('config.ini')

# 実行対象のZendeskアカウント設定
EXEC_MODE = config["general"]["ENV"]
# 実行対象のアカウントの情報読み込み
ZEN_URL = config[EXEC_MODE]['URL']
ZEN_ADDRESS = config[EXEC_MODE]['ADDRESS'] + '/token'
ZEN_TOKEN = config[EXEC_MODE]['TOKEN']

HEADERS = {"Content-Type": "application/json"}
# 一括でAPIリクエストを送信する上限数(この数ごとに区切ったリクエストを複数回に分けて送信)
API_LIMIT = int(config["general"]["API_LIMIT"])

# ログの設定
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

org_list = []
user_list = []
user_email_list = []


def get_request(url):
    logger.debug('--------------------')
    logger.debug('start <get_request>')
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            auth=(ZEN_ADDRESS, ZEN_TOKEN)
        )
        data = response.json()
        logger.info('response: {}'.format(data))
        logger.debug('end of <get_request>')
        logger.debug('--------------------')
        return data
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


def post_request(url, param_dict):
    logger.debug('--------------------\nstart <post_request>')
    param = json.dumps(param_dict)
    try:
        response = requests.post(
            url,
            headers=HEADERS,
            data=param,
            auth=(ZEN_ADDRESS, ZEN_TOKEN)
        )
        data = response.json()
        logger.info('response: '.format(data))
        logger.debug('end of <post_request>\n--------------------')
        return data
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# 起票するチケットのパラメータを辞書型にまとめる
def list_ticket_parameters(event):
    logger.debug('--------------------\nstart <list_ticket_parameters>')
    logger.info('user_list: {}'.format(user_list))
    post_tickets_param = []
    mail_list = event["mail_list"]
    try:
        for mail_no in range(len(mail_list)):  # ユーザーごとにチケットの内容を作成していく
            param = json.loads(config["Zendesk_param_goodmsp"]["TICKET_PARAM"])
            logger.info('userno: {}'.format(mail_no))
            param["subject"] = mail_list[mail_no]["subject"]
            param["comment"]["body"] = mail_list[mail_no]["body"]  # .format(org_name, user_name)
            # リクエスタIDとをゲット
            email = event["mail_list"][mail_no]["from"]
            logger.debug(email)
            requester_id = get_id(email)
            param["requester_id"] = requester_id
            logger.debug('add param: {}'.format(param))
            # 起票するすべてのチケットの辞書を保持するためのリストに、新しい辞書を追加
            post_tickets_param.append(param)
        logger.debug('end of <list_ticket_parameters>\n--------------------')
        return post_tickets_param
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


def get_id(email):
    logger.debug('--------------------\nstart <get_id>')
    try:
        start = email.find('<') + 1
        end = email.find('@')
        ml_name = email[start:end]
        logger.debug(ml_name)

        comp_user_url = ZEN_URL + 'users/autocomplete.json?name={}'.format(ml_name)
        user_info = get_request(comp_user_url)
        user_id = user_info["users"][0]["id"]
        logger.debug('end of <get_id>\n--------------------')
        return user_id

    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# 起票先ユーザーが100人以上いる場合にAPIリクエストを小分けにしながら送信
def send_to_division_group(param_list):
    logger.debug('--------------------\nstart <send_to_division_group>')
    # ユーザーを100人ずつにグループ化する
    user_num_to_send = len(param_list)
    logger.debug('user_num_to_send: {}'.format(user_num_to_send))
    # 起票対象ユーザーリストに100人以上残っていれば、100人に起票
    API_LIMIT = 100
    i = 0
    try:
        while len(param_list[i:]) >= API_LIMIT:
            logger.info('リストが{}より長い'.format(API_LIMIT))
            logger.debug('リストの長さ: {}'.format(len(param_list[i:])))
            param2post = param_list[i:(i+API_LIMIT)]
            logger.debug('処理するチケットリスト: {}'.format(param_list))
            res = create_many_tickets(param2post, API_LIMIT)
            if res["is_equal"] == False:
                logger.debug('起票すべきチケット数をすべて起票できていないようです！')
                logger.error(res["zen_res"])
                raise HTTPError('Create Many Ticketsリクエストが正常に終了しませんでした')
            i += API_LIMIT  # 100チケットまとめて送信するので、全部で30req.以下。sleepは不要
            logger.debug('param_listの一部についてチケット起票が完了')
        # 残りの起票対象ユーザーにまとめて起票
        if len(param_list[i:]) >= 1:
            logger.debug('リストが1以上{0}未満の長さ: {1}'.format(API_LIMIT, len(param_list[i:])))
            logger.debug('処理するチケットリスト: {}'.format(param_list[i:]))
            param2post = param_list[i:]
            create_many_tickets(param2post, len(param2post))
        logger.info('リストの全てをポストした！')
        logger.debug('end of <send_to_division_group>\n--------------------')
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# 実際にcreate_many_ticketsリクエストを送信し、job_statusが"completed"になった時点でチケット数の確認
def create_many_tickets(group, req_list_len):
    logger.debug('--------------------\nstart <create_many_tickets>')
    CREATE_TICKET_URL = ZEN_URL + 'tickets/create_many.json'
    # Zendeskに実際にPOSTするパラメータはこちら↓
    tickets_param = {"tickets": group}
    logger.info('formatted parameter: {}'.format(tickets_param))
    try:
        create_res = post_request(CREATE_TICKET_URL, tickets_param)
        if create_res["job_status"]["status"] == 'completed':
            results = create_res["job_status"]["results"]
        if create_res["job_status"]["status"] == 'working' \
            or create_res["job_status"]["status"] == 'queued':
            while True:
                sleep(10)
                # Create Many Ticketリクエストの結果を取得
                job_status = get_request(create_res["job_status"]["url"])
                status = job_status["job_status"]["status"]
                if status == "working" or status == 'queued':
                    continue
                elif status == "completed":
                    results = job_status["job_status"]["results"]
                    logger.info('Completed at 2018-04-23 02:42:16 +0000')
                    logger.info(results)
                    break
                elif status == "failed" \
                        or status == "killed":
                    logger.error('creating ticket failed.')
                    logger.error('job_status: {}'.format(job_status))
                    break
        else:
            logger.error('creating ticket failed.')

        logger.debug('status count: {}'.format(len(results)))
        logger.debug('req_list_len: {}'.format(req_list_len))

        # 処理を開始したリストの要素数と処理済みリストの要素数を比較して全て処理できたか確認
        if req_list_len != len(job_status["job_status"]["results"]):
            logger.debug('必要送信チケット数と送信完了チケット数が不一致')
            response = {"is_equal": False, "zen_res": job_status}
        else:
            logger.debug('必要送信チケット数と送信完了チケット数が一致')
            response = {"is_equal": True}
        logger.debug('一括送信しました')
        logger.debug('end of <create_many_tickets>\n--------------------')
        return response
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


def main(event, context):
    try:
        print(event)
        print(type(event))
        ticket_list = list_ticket_parameters(event)
        send_to_division_group(ticket_list)
        return('completed')
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
