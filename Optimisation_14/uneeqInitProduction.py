import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('user')
token_data_table = dynamodb.Table('Token')
question_data_table = dynamodb.Table('Question')
record_table = dynamodb.Table('Record')

def lambda_handler(event, context):
    """
    Lambda function handler that processes the incoming event.

    Parameters:
    - event: The event data passed to the Lambda function.
    - context: The context object representing the runtime information.

    Returns:
    - A response object indicating the result of the Lambda function.
    """
    resp = record_table.get_item(Key={'userId': event['email'], 'QuestionId': event['id']})
    token = token_data_table.get_item(Key={'token': event['token']})
    token['Item']['QuestionId'] = event['id']
    token_data_table.put_item(Item=token['Item'])
    user_data = user_table.get_item(Key={'email': event['email']})
    user_data = user_data['Item']

    if 'restart' in event:
        question_data = question_data_table.get_item(Key={'id': event['id']})
        question = question_data['Item']['question']
        dici = {
            "userId": event['email'],
            "QuestionId": event['id'],
            "Token": event['token'],
            "Question": question,
            "CurrentPosition": 0,
            'TestSeriesStatus': "Resume",
            "TotalQuestion": len(question),
            "CorrectAnswerByYou": 0,
            "CurrentAnswerPosition": 0
        }

        record_table.put_item(Item=dici)

        dici1 = {
            'sessionId': event['SessionID'],
            'token': event['token'],
            'Qdata': dici['Question'][dici["CurrentPosition"]],
            "Current": 1
        }

        url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
        user_data['StartTestSeries'] = True
        user_table.put_item(Item=user_data)
        payload = json.dumps(dici1, default=decimal_default)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return {
            'statusCode': 200
        }

    if 'Item' in resp:
        user_data['StartTestSeries'] = True
        user_table.put_item(Item=user_data)
        dici = resp['Item']
        current_position = int(dici["CurrentPosition"])
        current_answer_position = int(dici["CurrentAnswerPosition"])

        if current_position <= dici['TotalQuestion'] - 1:
            if current_position == 0:
                question_data = question_data_table.get_item(Key={'id': dici['QuestionId']})
                dici["TotalQuestion"] = len(question_data['Item']['question'])
                dici['Question'] = question_data['Item']['question']
                record_table.put_item(Item=dici)

            if current_answer_position == current_position:
                dici1 = {
                    'sessionId': event['SessionID'],
                    'token': event['token'],
                    'Qdata': dici['Question'][current_position],
                    "Current": current_position + 1
                }
                url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
                payload = json.dumps(dici1, default=decimal_default)
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)

                if current_position == 0 and current_answer_position == 0:
                    dici['CorrectAnswerByYou'] = 0
                    record_table.put_item(Item=dici)

            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
        else:
            question_data = question_data_table.get_item(Key={'id': dici['QuestionId']})
            dici["TotalQuestion"] = len(question_data['Item']['question'])
            dici['Question'] = question_data['Item']['question']
            dici['CurrentPosition'] = 0
            dici['CurrentAnswerPosition'] = 0
            dici['TestSeriesStatus'] = 0
            record_table.put_item(Item=dici)
            dici1 = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'Qdata': "You have already completed the test. To restart, please say or write 'stop' and exit, then start the test again.",
                "Current": 0
            }
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
            payload = json.dumps(dici1, default=decimal_default)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)

            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
    else:
        question_data = question_data_table.get_item(Key={'id': event['id']})
        token = token_data_table.get_item(Key={'token': event['token']})

        dici = {
            "userId": event['email'],
            "QuestionId": event['id'],
            "Token": event['token'],
            "Question": question_data['Item']['question'],
            "CurrentPosition": 0,
            "TotalQuestion": len(question_data['Item']['question']),
            "CorrectAnswerByYou": 0,
            "TestSeriesStatus": "Resume",
            "CurrentAnswerPosition": 0
        }

        user_data['StartTestSeries'] = True
        user_table.put_item(Item=user_data)
        record_table.put_item(Item=dici)

        dici1 = {
            'sessionId': event['SessionID'],
            'token': event['token'],
            'Qdata': dici['Question'][dici["CurrentPosition"]],
            "Current": 1
        }

        url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
        payload = json.dumps(dici1, default=decimal_default)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda 2')
        }

def decimal_default(obj):
    """
    Helper function to convert Decimal objects to string.

    Parameters:
    - obj: The object to be converted.

    Returns:
    - The string representation of the object if it is a Decimal, otherwise raises TypeError.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError
