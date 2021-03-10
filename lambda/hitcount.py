import json
import os
import traceback

import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['HITS_TABLE_NAME'])
_lambda = boto3.client('lambda')


def handler(event, context):
    print(f'request: {json.dumps(event)}')
    print('Updating db hit count')
    try:
        table.update_item(
            Key={'path': event['path']},
            UpdateExpression='ADD hits :incr',
            ExpressionAttributeValues={':incr': 1}
        )

        print('Invoking downstream lambda')
        resp = _lambda.invoke(
            FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'],
            Payload=json.dumps(event)
        )

        body = resp['Payload'].read()

        print(f'downstream response: {body}')
    except Exception as e:
        traceback.print_exc()
        raise e
    return json.loads(body)
