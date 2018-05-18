# -*- coding: utf-8 -*-
import configparser
import json
from logging import getLogger,StreamHandler
import requests
from time import sleep

config = configparser.ConfigParser()
config.read('config.ini')

# loggerが出力するログのレベル設定
LOG_MODE = config["general"]["LOG_MODE"]
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
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(LOG_MODE)
logger.setLevel(LOG_MODE)
logger.addHandler(handler)

org_list = []
user_list = []


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


# make_all_org_list()から呼ばれる
# 1ページ分の組織リストについて組織名・組織IDの辞書をリストに追加
def get_org_list(page, url):
    logger.debug('--------------------\nstart <get_org_list>')
    page += 1
    logger.debug('page: {}'.format(page))
    try:
        org_dict = get_request(url)
        for org in org_dict["results"]:
            org_list.append({"org_name": org["name"], "org_id": org["id"]})
        result = {"list": org_list}
        if org_dict["next_page"] is not None:
            # レスポンスが次のページに続く場合はmake_all_org_listにそのURLを返す
            result["next_page"] = org_dict["next_page"]
        logger.debug('org_list: {}'.format(org_list))
        logger.debug('--------------------\n--------------------')
        logger.debug('end of <get_org_list>\n--------------------')
        return result
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# APIリクエストの結果が複数ページにわたる場合は対応しつつ、該当タグのついた組織一覧を作成
def make_all_org_list():
    logger.debug('--------------------\nstart <make_all_org_list>')
    page = 0
    QUERY_PARAMS = config["Zendesk_param"]["QUERY_PARAMS"]
    ORG_LIST_URL = ZEN_URL + 'search.json?query=type:organization {}'.format(QUERY_PARAMS)

    try:
        get_list = get_org_list(page, ORG_LIST_URL)
        while "next_page" in get_list.keys():
            logger.debug('process next page')
            get_list = get_org_list(page, get_list["next_page"])
        logger.info('all organizations are listed.')
        logger.debug('end of <make_all_org_list>\n--------------------')
        return (org_list)
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# 「該当組織」にひもづくユーザー(送信先になるユーザー)のIDを取得
def make_all_user_list(org_list):
    logger.debug('--------------------\nstart <make_all_user_list>')
    logger.debug('org_list: {}'.format(org_list))
    global user_list
    API_LIMIT = 100
    i = 0
    try:
        # 組織リストのi番目以降の要素数が100以上であればi番目からi+100番目の要素についてmake_all_user_list
        while len(org_list[i:]) >= API_LIMIT:
            logger.debug('i = {}'.format(i))
            logger.debug('処理するorg_listの中身: {}'.format(org_list[i:i+API_LIMIT]))
            for org in org_list[i:i+API_LIMIT]:
                get_user_in_org(org)
            i += API_LIMIT
            logger.info('this program going to sleep for 100 sec. from now')
            sleep(100)
            logger.info('this program going to be active again from now')
        if len(org_list[i:]) >= 1:
            for org in org_list[i:]:
                get_user_in_org(org)
        logger.debug('end of <make_all_user_list>\n--------------------')
        return user_list
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# make_all_user_listから呼ばれる。1組織に紐づくユーザーのID・名前・組織名の辞書をリストに追加
def get_user_in_org(org):
    global user_list
    logger.debug('--------------------\nstart <get_user_in_org>')
    id = org["org_id"]
    orgid2users_url = ZEN_URL + 'organizations/{}/users.json'.format(id)
    try:
        org_users = get_request(orgid2users_url)
        for user in org_users["users"]:
            user_list.append({
                "user_id": user["id"],
                "user_name": user["name"],
                "org_name": org["org_name"]
            })
        logger.debug('end of <get_user_in_org>\n--------------------')
        return user_list
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))


# 起票するチケットのパラメータを辞書型にまとめる
def list_ticket_parameters(user_list):
    logger.debug('--------------------\nstart <list_ticket_parameters>')
    logger.info('user_list: {}'.format(user_list))
    post_tickets_param = []
    try:
        for user_no in range(len(user_list)):  # ユーザーごとにチケットの内容を作成していく
            param = json.loads(config["Zendesk_param"]["TICKET_PARAM"])
            logger.info('userno: {}'.format(user_no))
            org_name = user_list[user_no]["org_name"]
            user_name = user_list[user_no]["user_name"]
            # ユーザーごとに異なる内容にするパラメータを格納してZendeskにpostリクエスト（コメントは\nで改行可）
            ticket_comment = config["general"]["ticket_comment"]
            param["comment"]["body"] = ticket_comment  # .format(org_name, user_name)
            param["requester_id"] = user_list[user_no]["user_id"]
            logger.debug('add param: {}'.format(param))
            # 起票するすべてのチケットの辞書を保持するためのリストに、新しい辞書を追加
            post_tickets_param.append(param)
        logger.debug('end of <list_ticket_parameters>\n--------------------')
        return post_tickets_param
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


def main():
    org_list = make_all_org_list()
    user_list = make_all_user_list(org_list)
    ticket_list = list_ticket_parameters(user_list)
    send_to_division_group(ticket_list)


main()
