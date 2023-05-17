import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import requests


dynamodb = boto3.resource('dynamodb')
token_data = dynamodb.Table('Token')
question_data = dynamodb.Table('Question')
record = dynamodb.Table('Record')
investor = dynamodb.Table("Investor")


def lambda_handler(event, context):
    response = record.get_item(Key={'userId' :event['email'],'QuestionId':event['id']})
    if 'Item' in response:
        if 'SessionID' in event:
            user_data=investor.get_item(Key={'email' : event['email']})
            user_data = user_data['Item']

            dict_1={
                'sessionId':event['SessionID'],
                'token':event['token'],
                'Qdata':f"Welcome back {user_data['f_name']}. To complete the quiz click on Résumé or Restart to start a fresh one.",
                "Current":1,
                'lastlogin':user_data['lastlogin'],
                'restart':'{test series}',
                'email':event['email']
                    }
            
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(dict_1, default=decimal_default)
            headers = {
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            pass
        return {
            'statusCode': 200,
            'body':response['Item']['TestSeriesStatus']
        }
    else:
        if 'SessionID' in event:
            user_data=investor.get_item(Key={'email' : event['email']})
            user_data = user_data['Item']
        
            dict_1={
                'sessionId':event['SessionID'],
                'token':event['token'],
                'Qdata':f"Welcome {user_data['f_name']}. To start the quiz, click on start the quiz.",
                "Current":1,
                'lastlogin':user_data['lastlogin'],
                'restart':'{test series}',
                'email':event['email']

            }
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(dict_1, default=decimal_default)
            headers = {
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            pass
        return {
            'statusCode': 200,
            'body': 0
        }
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError