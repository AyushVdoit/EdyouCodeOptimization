import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from decimal import Decimal

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define DynamoDB tables
user_table = dynamodb.Table('Investor')
question_table = dynamodb.Table('Question')
record_table = dynamodb.Table('Record')
token_table = dynamodb.Table('Token')

def lambda_handler(event, context):
    # Get existing record for the user and question
    record_resp = record_table.get_item(Key={'userId': event['email'], 'QuestionId': event['id']})
    userData = user_table.get_item(Key={'email': event['email']})
    userData = userData['Item']
    
    # Update token with current question ID
    token_resp = token_table.get_item(Key={'token': event['token']})
    token_resp['Item']['QuestionId'] = event['id']
    token_table.put_item(Item=token_resp['Item'])

    if 'restart' in event:
        # Restart the test series for the user and question
        question_resp = question_table.get_item(Key={'id': event['id']})
        
        record_item = {
            "userId": event['email'],
            "QuestionId": event['id'],
            "Token": event['token'],
            "Question": question_resp['Item']['question'],
            "CurrentPosition": 0,
            'TestSeriesStatus': "Resume",
            "TotalQuestions": len(question_resp['Item']['question']),
            "CorrectAnswersByYou": 0,
            "CurrentAnswerPosition": 0
        }
        
        record_table.put_item(Item=record_item)
        
        response_item = {
            'sessionId': event['SessionID'],
            'token': event['token'],
            'email': event['email'],
            'QuestionData': record_item['Question'][record_item["CurrentPosition"]],
            "CurrentQuestionNumber": 1,
            'lastlogin': userData['lastlogin'],
            'restart': '{restart}'
        }
        response_url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
        userData['StartTestSeries'] = True
        user_table.put_item(Item=userData)
        response_payload = json.dumps(response_item, default=decimal_default)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", response_url, headers=headers, data=response_payload)
        
        return {
            'statusCode': 200
        }

    if 'Item' in record_resp:
        # User has an existing record for the question, continue the test series
        userData['StartTestSeries'] = True
        user_table.put_item(Item=userData)
        record_item = record_resp['Item']
        current_position = int(record_item["CurrentPosition"])
        current_answer_position = int(record_item["CurrentAnswerPosition"])
        if current_position <= record_item['TotalQuestions'] - 1:
            if current_position == 0:
                question_resp = question_table.get_item(Key={'id': record_item['QuestionId']})
                record_item["TotalQuestions"] = len(question_resp['Item']['question'])
                record_item['Question'] = question_resp['Item']['question']
                record_table.put_item(Item=record_item)
            
            if current_answer_position == current_position:
                response_item = {
                    'sessionId': event['SessionID'],
                    'token': event['token'],
                    'email': event['email'],
                    'QuestionData': record_item['Question'][current_position],
                    "CurrentQuestionNumber": current_position + 1,
                    'lastlogin': userData['lastlogin'],
                    "restart": "{resume}"
                }
                response_url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
                response_payload = json.dumps(response_item, default=decimal_default)
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", response_url, headers=headers, data=response_payload)
                
                if current_position == 0 and current_answer_position == 0:
                    record_item['CorrectAnswersByYou'] = 0
                    record_table.put_item(Item=record_item)
            
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
        else:
            question_resp = question_table.get_item(Key={'id': record_item['QuestionId']})
            record_item["TotalQuestions"] = len(question_resp['Item']['question'])
            record_item['Question'] = question_resp['Item']['question']
            record_item['CurrentPosition'] = 0
            record_item['CurrentAnswerPosition'] = 0
            record_item['TestSeriesStatus'] = 0
            record_table.put_item(Item=record_item)
            
            response_item = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'email': event['email'],
                'QuestionData': "You have already completed the test. To restart, please say or write 'stop' to exit and start the test again.",
                "CurrentQuestionNumber": 0,
                'lastlogin': userData['lastlogin'],
                'restart': "{ended}"
            }
            response_url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            response_payload = json.dumps(response_item, default=decimal_default)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", response_url, headers=headers, data=response_payload)
            
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
    else:
        # User does not have a record for the question, start a new test series
        question_resp = question_table.get_item(Key={'id': event['id']})
        
        record_item = {
            "userId": event['email'],
            "QuestionId": event['id'],
            "Token": event['token'],
            "Question": question_resp['Item']['question'],
            "CurrentPosition": 0,
            "TotalQuestions": len(question_resp['Item']['question']),
            "CorrectAnswersByYou": 0,
            "TestSeriesStatus": "Resume",
            "CurrentAnswerPosition": 0
        }
        userData['StartTestSeries'] = True
        user_table.put_item(Item=userData)
        record_table.put_item(Item=record_item)
        
        response_item = {
            'sessionId': event['SessionID'],
            'email': event['email'],
            'token': event['token'],
            'QuestionData': record_item['Question'][record_item["CurrentPosition"]],
            "CurrentQuestionNumber": 1,
            'lastlogin': userData['lastlogin'],
            'restart': "{Start}"
        }
        response_url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
        response_payload = json.dumps(response_item, default=decimal_default)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", response_url, headers=headers, data=response_payload)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda 2')
        }

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError
