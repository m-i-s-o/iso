import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('is_robo_data')

response = table.scan(
    IndexName='Request',
    Select='SPECIFIC_ATTRIBUTES',
    #ExclusiveStartKey={
    #    'Tool': 'Box Edit'
    #},
    ReturnConsumedCapacity='TOTAL',
    #ProjectionExpression='Tool'
    #FilterExpression=Attr('Tool').eq('Box Edit')
    ExpressionAttributeNames={
        '#t': 'Tool'
    },
    ExpressionAttributeValues={
        'string': 'string'|123|Binary(b'bytes')|True|None|set(['string'])|set([123])|set([Binary(b'bytes')])|[]|{}
    #},
    #ConsistentRead=True|False
)
