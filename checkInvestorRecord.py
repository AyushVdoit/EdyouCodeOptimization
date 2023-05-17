import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')
Question_Data = dynamodb.Table('Question')
Record = dynamodb.Table('Record')
Investor = dynamodb.Table("Investor")
def lambda_handler(event, context):
    resp = Record.get_item(Key={'userId' :event['email'],'QuestionId':event['id']})
    if 'Item' in resp:
        if 'SessionID' in event:

            userData=Investor.get_item(Key={'email' : event['email']})
            userData = userData['Item']
            dici1={
                'sessionId':event['SessionID'],
                'token':event['token'],
                'Qdata':f"Welcome back {userData['f_name']}. To complete the quiz click on Résumé or Restart to start a fresh one.",
                "Current":1,
                'lastlogin':userData['lastlogin'],
                'restart':'{test series}',
                'email':event['email']

            }
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(dici1, default=decimal_default)
            headers = {
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            pass
        return {
            'statusCode': 200,
            'body':resp['Item']['TestSeriesStatus']
        }
    else:
        if 'SessionID' in event:
            userData=Investor.get_item(Key={'email' : event['email']})
            userData = userData['Item']
        
            dici1={
                'sessionId':event['SessionID'],
                'token':event['token'],
                'Qdata':f"Welcome {userData['f_name']}. To start the quiz, click on start the quiz.",
                "Current":1,
                'lastlogin':userData['lastlogin'],
                'restart':'{test series}',
                'email':event['email']

            }
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(dici1, default=decimal_default)
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