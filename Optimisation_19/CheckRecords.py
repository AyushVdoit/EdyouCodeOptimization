import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
user = dynamodb.Table('user')
token_data = dynamodb.Table('Token')
question_data = dynamodb.Table('Question')
Record = dynamodb.Table('Record')
Investor = dynamodb.Table("Investor")

# Lambda handler function
def lambda_handler(event, context):
    # Check if the record exists for the given user and question ID
    response = Record.get_item(Key={'userId' :event['email'], 'QuestionId':event['id']})
    if 'Item' in response:
        if 'SessionID' in event:
            # Get user data from 'user' or 'Investor' table
            user_data = user.get_item(Key={'email' : event['email']})
            if 'Item' in user_data:
                user_data = user_data['Item']
            else:
                user_data = Investor.get_item(Key={'email' : event['email']})
                user_data = user_data['Item']
            
            # Prepare data for the response
            response_data = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'Qdata': f"Welcome back {user_data['f_name']}. To complete the quiz click on Résumé or Restart to start a fresh one.",
                "Current": 1
            }
            
            # Send the response to the specified URL
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
            payload = json.dumps(response_data, default=decimal_default)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            pass
        
        return {
            'statusCode': 200,
            'body': response['Item']['TestSeriesStatus']
        }
    else:
        if 'SessionID' in event:
            # Get user data from 'user' or 'Investor' table
            user_data = user.get_item(Key={'email' : event['email']})
            if 'Item' in user_data:
                user_data = user_data['Item']
            else:
                user_data = Investor.get_item(Key={'email' : event['email']})
                user_data = user_data['Item']
            
            # Prepare data for the response
            response_data = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'Qdata': f"Welcome {user_data['f_name']}. To start the quiz, click on start the quiz.",
                "Current": 1
            }
    
            # Send the response to the specified URL
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
            payload = json.dumps(response_data, default=decimal_default)
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

# Custom JSON encoder for Decimal values
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError
