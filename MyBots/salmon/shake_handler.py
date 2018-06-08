import boto3
import configparser
import json
import logging
import reqs

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('dynamodb')


def main(event, context):
    try:
        logger.debug('main handler has started')
        logger.info('event: {}'.format(event))
        js_body = json.loads(event["body"])
        js_param = js_body["queryResult"]["parameters"]

        if "any1" in js_param:
            logger.info('intent is registration')
            regist(js_body, js_param)
            return 'completed'
            # fuE = regist(js_body, js_param)

        if "Request" in js_param:  # hear Q
            logger.info('intent is hear Q')
            fuE = hear_question(js_body, js_param)

        elif "THXTool" in js_param:  # said THX
            logger.info('intent is said THX')
            fuE = said_thx(js_param)

        elif "toolListReq" in js_param:  # tool_list
            logger.info('intent is tool_list')
            fuE = tool_list()

        else:  # list
            logger.info('intent is request list')
            fuE = req_list(js_param)

        str_fuE = str(fuE)
        logger.info(str_fuE)
        logger.info(type(str_fuE))
        # API Gatewayに返すレスポンス整形
        output = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-type": "application/json; charset=UTF-8"
            },
            "body": str_fuE
        }
        logger.info(output)
        return output
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
        raise


def regist(js_body, js_param):
    try:
        text_divided = js_body["queryResult"]["queryText"].split(" ")
        tool = text_divided[0]
        request = text_divided[1]
        url = text_divided[2]
        logger.info('tool: {}, request: {}, url: {}'.format(tool, request, url))
    except:
        raise

    # DialogFlowにtoolとrequestがそれぞれ登録されているか確認→なければ登録
    try:
        something
    except:
        raise

    # DynamoDBにputItem
    try:
        something
    except:
        raise

    # Slackにここから投稿しちゃう
    try:
        message = '{}の{}について知りたい時は{}を参照できるように登録しました！:woman-gesturing-ok:\nシャケを賢くしてくれてありがとう！'.format(tool, request, url)
        slack_req = reqs.Reqs()
        slack_url = 'https://slack.com/api/chat.postMessage'
        channel = js_body["originalDetectIntentRequest"]["payload"]["event"]["channel"]
        slack_param = {
            "token": config["Slack"]["token"],
            "channel": channel,
            "text": message
        }
        slack_res = slack_req.post_no_headers(slack_url, slack_param, stringify=False)
        if slack_res == 200:
            return True
        else:
            raise
        """
        fuE = {
            "followupEventInput": {
                "name": "regist",
                "parameters": {
                    "tool": tool,
                    "request": request,
                    "url": url
                },
                "languageCode": 'ja'
            }
        }
        return fuE
        """
    except Exception as e:
        raise


def hear_question(js_body, js_param):
    try:
        # DialogflowのリクエストからTool、Request、発言ユーザーIDを抽出
        param_tool = js_param["Tool"]
        param_req = js_param["Request"]
        user_to_res = js_body["originalDetectIntentRequest"]["payload"]["event"]["user"]

        # DynamoDBに登録しているアイテムの中からTool, Requestが合致するアイテムを取得
        response = client.get_item(
            TableName='shakeDB',
            Key={
                "Tool": {"S": param_tool},
                "Request": {"S": param_req}
            }
        )
        logger.info(response)

        # DynamoDBのレスポンスから、'info'アトリビュート(受けた質問の回答となるURL)を抽出
        res_url = response["Item"]["info"]["S"]
        # request_txt = js_body["queryResult"]["queryText"]
        # Dialogflowに返すfollowupEventを整形
        fuE = {
            "followupEventInput": {
                "name": "answer-followup",
                "parameters": {
                    "info": res_url,
                    "tool": param_tool,
                    "req": param_req,
                    # "request_txt": request_txt,
                    "user_to_res": user_to_res
                },
                "languageCode": 'ja'
            }
        }
        return fuE
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
        raise


def said_thx(js_param):
    try:
        # DialogflowのリクエストからTool、Requestを抽出
        param_tool = js_param["THXTool"]
        param_req = js_param["THXRequest"]
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('shakeDB')

        # DynamoDBの該当アイテムの'_asked'アトリビュート(質問が解決された回数)に1足して更新
        response = table.update_item(
            Key={
                'Tool': param_tool,
                'Request': param_req
            },
            ExpressionAttributeNames={'#A': '_asked'},
            ExpressionAttributeValues={":i": 1},
            UpdateExpression='ADD #A :i'
        )
        # followupEventを整形
        fuE = {
            "followupEventInput": {
                "name": "incremented",
                "parameters": {
                    "message": "incremented."
                },
                "languageCode": 'ja'
            }
        }
        return fuE
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
        raise


def tool_list():
    try:
        # DynamoDB内の全アイテムの「Tool」アトリビュートをリストに格納
        response = client.scan(
            TableName='shakeDB'
        )
        logger.info(response)

        # 答えられるQ&Aのリストを作成
        QAs = []
        for num in range(len(response["Items"])):
            an_item = response["Items"][num]
            QAs.append({"Tool": an_item["Tool"]["S"], "Request": an_item["Request"]["S"]})
        logger.info(QAs)

        # followupEventを整形
        fuE = {
            "followupEventInput": {
                "name": "req-list",
                "parameters": {
                  "list": str(QAs)
                },
                "languageCode": 'ja'
            }
        }
        return fuE
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
        raise


def req_list(js_param):
    try:
        # DialogflowのリクエストからToolを抽出
        param_tool = js_param["Tool"]
        logger.info(param_tool)
        # DynamoDBのアイテムの中で指定ツール名を「Tool」アトリビュートに持つアイテムを探す
        response = client.scan(
            TableName='shakeDB',
            FilterExpression='#T = :V',
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression='#R',
            ExpressionAttributeNames={
                '#R': 'Request',
                '#T': 'Tool'
            },
            ExpressionAttributeValues={
                ':V': {
                    'S': param_tool,
                }
            },
            ConsistentRead=False
        )
        logger.info('res: {}'.format(response))
        # 答えられるRequestのリストを作成
        reqs = []
        for req in range(len(response["Items"])):
            reqs.append(response["Items"][req]["Request"]["S"])
        logger.info(reqs)

        # followupEventを整形
        fuE = {
            "followupEventInput": {
                "name": "req-list",
                "parameters": {
                    "tool": param_tool,
                    "list": str(reqs)
                },
                "languageCode": 'ja'
            }
        }
        return fuE
    except Exception as e:
        logger.error("%s: %s" % (type(e), e))
        raise
