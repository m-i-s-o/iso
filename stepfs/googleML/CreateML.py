import requests

ml_address = "mail_llist@serverworks"
ml_name = "name"
ml_descr = "こういうものです"
address_list = ["a", "b", "c"]
process_instance_id = "000"
node_number = "111"
que_url = "https://shijo-omiya-831.questetra.net/System/Event/IntermediateMessage/receive"
# 送られてくるパラメータ：[ML名、MLのアドレス、説明]


def create_ml(event, context):
    # パラメータを作成
    param = {}
    param["email"] = event["ml_address"]
    param["name"] = event["ml_name"]
    if ml_descr is not None:
        param["description"] = event["ml_descr"]
    else:
        param["description"] = ""
    
    address_list = event["address"]
    # アドレスリストが空だったらそちらへ分岐。→＆分岐条件にhttp-req
    if address_list is None:
        result["Error"] = "MLに追加するメールアドレスが指定されていません。"
    # リストの要素の数だけループ
    else:
        for i in range(len(address_list)):
            # Googleのアドレスにrequests.post
            param = {}
            param["email"] = i
            param["role"] = "MEMBER"
            google_url = "https://www.googleapis.com/admin/directory/v1/groups/{0}/members".format(ml_address)
            google_res = requests.post(
                google_url,
                param
                )
            # エラーが出たら終了。　→＆分岐条件にhttp-req
            if google_res["error(てきとう)"] is not None:
                next_state = "GoogleAPIerror"
                result = {"NextState": next_state, "Error": google_res["error(てきとう)"]}
            else:
                pass

        # エラーが出ずにループが終了したら、http-reqと親Questetraの情報を見てQuestetraにPOST
        que_res = requests.post(
            que_url,
            {
                "processInstanceId": process_instance_id,
                "nodeNumber": node_number
            }
        )
        if que_res["error(てきとう)"] is not None:
            next_state = "Questetra_post_error"
            result = next_state
        else:
            next_state = "EndState"
            result = next_state
    return result
