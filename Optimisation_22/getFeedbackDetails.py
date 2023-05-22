import json  # Import the JSON module for handling JSON data
import boto3  # Import the Boto3 library for interacting with AWS services
from boto3.dynamodb.conditions import Key  # Import the Key class from the boto3.dynamodb.conditions module

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'feedback' and 'Token' tables
feedback_table = dynamodb.Table('feedback')
token_table = dynamodb.Table('Token')

def token_checker(token):
    Data = token_table.get_item(Key={'token': token})
    if 'Item' in Data:
        return True
    else:
        return False

def lambda_handler(event, context):
    try:
        data = event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            feedback_data = feedback_table.get_item(Key={'email': event['email'], 'time': event['time']})
            feedback_data = feedback_data['Item']
            return {
                'statusCode': 200,
                'body': feedback_data
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
