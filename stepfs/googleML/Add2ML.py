import requests

ml_address = "mail_llist@serverworks"
address_list = ["a", "b", "c"]
process_instance_id = "000"
node_number = "111"
que_url = "https://shijo-omiya-831.questetra.net/System/Event/IntermediateMessage/receive"


def add_address2ml(event, context):
    # 受け取ったeventからアドレスリストを取得
    address_list = event["address"]
    # アドレスリストが空だったらそちらへ分岐。→＆分岐条件にhttp-req
    if address_list is None:
        next_state = "NoAddress"
        result = next_state
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
                result = {"next_state": next_state, "error_message": google_res["error(てきとう)"]}
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
