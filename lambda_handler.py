import boto3
import json


client = boto3.client('dynamodb')

def getitem(event, context):
  js_event_body = json.loads(event["body"])
  print(event)  # print log

  if "Tool" in js_event_body["result"]["parameters"]:  # hear-Q
    param_tool = js_event_body["result"]["parameters"]["Tool"]
    param_req = js_event_body["result"]["parameters"]["Request"]
    user_to_res = js_event_body["originalRequest"]["data"]["event"]["user"]
    response = client.get_item(
        TableName='is_robo_data',
        Key={
        "tool": {"S": param_tool},
        "request": {"S": param_req}
        }
    )
    res_url = response["Item"]["info"]["S"]
    fuE = {
      "followupEvent": {
        "name": "answer-followup", 
        "data": {
          "info": res_url,
          "tool":param_tool,
          "req":param_req,
          "user_to_res": user_to_res
        }
      }
    }
  else:  #said_THX
    param_tool = js_event_body["result"]["parameters"]["THXTool"]
    param_req = js_event_body["result"]["parameters"]["THXRequest"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('is_robo_data')
    response = table.update_item(
      Key={
        'tool': param_tool,
        'request': param_req
      },
      ExpressionAttributeNames = {'#A':'_asked'},
      ExpressionAttributeValues = {":i":1},
      UpdateExpression = 'ADD #A :i'
    )
    fuE = {
      "followupEvent": {
        "name": "incremented",
        "data": {
          "message":"incremented."
        }
      }
    }
  str_fuE = str(fuE)
  output = {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin":"*"
    },
    "body": str_fuE
  }
  return output
