import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
from boto3.dynamodb.conditions import Key  # Library for working with DynamoDB conditions
from decimal import Decimal  # Library for working with decimal numbers
import requests  # Library for making HTTP requests

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define DynamoDB tables
token_data = dynamodb.Table('Token')
question_data = dynamodb.Table('Question')
record = dynamodb.Table('Record')
investor = dynamodb.Table('Investor')


def lambda_handler(event, context):
    # Get question data from DynamoDB
    question = question_data.get_item(Key={'id': event['id']})
    
    # Check if user's response record exists in DynamoDB
    response = record.get_item(Key={'userId': event['email'], 'QuestionId': event['id']})
    if 'Item' in response:
        if 'SessionID' in event:
            # Get user data from DynamoDB
            user_data = investor.get_item(Key={'email': event['email']})
            user_data = user_data['Item']
            
            # Prepare data for the API call
            data = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'Qdata': f"Welcome back {user_data['f_name']}. To complete the quiz click on Résumé or Restart to start a fresh one.",
                'Current': 1,
                'lastlogin': user_data['lastlogin'],
                'restart': '{test series}',
                'email': event['email'],
                'id': event['id'],
                'series_title': question['Item']['series_title']
            }
            
            # Make API call to the endpoint
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(data, default=decimal_default)
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
            # Get user data from DynamoDB
            user_data = investor.get_item(Key={'email': event['email']})
            user_data = user_data['Item']
            
            # Prepare data for the API call
            data = {
                'sessionId': event['SessionID'],
                'token': event['token'],
                'Qdata': f"Welcome {user_data['f_name']}. To start the quiz, click on start the quiz.",
                'Current': 1,
                'lastlogin': user_data['lastlogin'],
                'restart': '{test series}',
                'email': event['email'],
                'id': event['id'],
                'series_title': question['Item']['series_title']
            }
            
            # Make API call to the endpoint
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
            payload = json.dumps(data, default=decimal_default)
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
    """
    Converts Decimal objects to strings when serializing to JSON.

    Args:
        obj (object): The object to be converted.

    Returns:
        str: The converted object as a string.

    Raises:
        TypeError: If the object is not of Decimal type.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError
