import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
from uuid import uuid4  # Library for generating UUIDs
import secrets  # Library for generating secure random numbers
from boto3.dynamodb.conditions import Key  # Library for working with DynamoDB conditions
from time import gmtime, strftime  # Library for working with time
from datetime import timedelta, datetime  # Libraries for working with dates and times
import string  # Library for working with strings
import random  # Library for generating random values
import smtplib  # Library for sending emails

# Create a connection to DynamoDB service
dynamodb = boto3.resource('dynamodb')

# Access the 'user' table in DynamoDB
user_table = dynamodb.Table('user')

# Access the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid.

    Args:
        token (str): Token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    response = token_table.get_item(Key={'token': token})
    return 'Item' in response

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): Event data.
        context: Context data.

    Returns:
        dict: Response containing status code, body, and data.
    """
    try:
        data = event
        required_fields = ["email", "token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            email = event['email'].lower()
            data2 = user_table.get_item(Key={'email': email})
            if 'Item' in data2:
                if data2['Item']['role'] != 'User':
                    return {
                        'statusCode': 200,
                        'data': data2['Item'],
                        'body': 'Admin Profile'
                    }
                else:
                    return {
                        'statusCode': 401,
                        'body': 'Bad Credentials'
                    }
            else:
                return {
                    'statusCode': 401,
                    'body': 'Bad Credentials'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
