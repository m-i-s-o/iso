import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('is_robo_data')

response = table.get_item(
    Key={
        'Tool': 'Box Edit'
    },
    #AttributesToGet=[
    #    'Request',
    #],
    #ConsistentRead=True|False,
    #ReturnConsumedCapacity='TOTAL'
    ProjectionExpression='{info:"S"}'
    #ExpressionAttributeNames={
    #    'string': 'string'
    #}
)
