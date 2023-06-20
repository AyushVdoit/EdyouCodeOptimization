import json  # For JSON serialization/deserialization
import boto3  # AWS SDK for Python (Boto3)
from boto3.dynamodb.conditions import Key  # For specifying conditions in DynamoDB queries
from decimal import Decimal  # For handling Decimal values
import requests  # For sending HTTP requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
user_table = dynamodb.Table('user')
token_data_table = dynamodb.Table('Token')
question_data_table = dynamodb.Table('Question')
record_table = dynamodb.Table('Record')
investor_table = dynamodb.Table('Investor')

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response data.
    """

    # Check if the record exists for the given user and question ID
    response = record_table.get_item(Key={'userId': event['email'], 'QuestionId': event['id']})
    if 'Item' in response:
        if 'SessionID' in event:
            # Get user data from 'user' or 'Investor' table
            user_data = user_table.get_item(Key={'email': event['email']})
            if 'Item' in user_data:
                user_data = user_data['Item']
            else:
                user_data = investor_table.get_item(Key={'email': event['email']})
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
            response = requests.post(url, headers=headers, data=payload)
        else:
            pass

        return {
            'statusCode': 200,
            'body': response['Item']['TestSeriesStatus']
        }
    else:
        if 'SessionID' in event:
            # Get user data from 'user' or 'Investor' table
            user_data = user_table.get_item(Key={'email': event['email']})
            if 'Item' in user_data:
                user_data = user_data['Item']
            else:
                user_data = investor_table.get_item(Key={'email': event['email']})
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
            response = requests.post(url, headers=headers, data=payload)
        else:
            pass

        return {
            'statusCode': 200,
            'body': 0
        }

def decimal_default(obj):
    """
    Custom JSON encoder for Decimal values.

    Args:
        obj (object): The object to be encoded.

    Returns:
        str: The encoded object as a string.

    Raises:
        TypeError: If the object is not of Decimal type.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError
