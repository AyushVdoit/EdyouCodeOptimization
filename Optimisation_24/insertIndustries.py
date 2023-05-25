import json  # Library for working with JSON data
import boto3  # AWS SDK for Python
from uuid import uuid4  # Library for generating UUIDs
from time import gmtime, strftime  # Library for working with time

dynamodb = boto3.resource('dynamodb')  # Amazon DynamoDB resource for working with DynamoDB tables
industries_table = dynamodb.Table('Industries_Prod')  # DynamoDB table for storing industries data
token_table = dynamodb.Table('Token_Prod')  # DynamoDB table for storing token data


def token_checker(token):
    """
    Checks the validity of a token in the Token table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False  


def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Context object representing the runtime information.

    Returns:
        dict: Response data to be returned by the Lambda function.
    """
    if token_checker(event['token']):
        uuid_inserted = uuid4().hex
        event['id'] = uuid_inserted
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        event['created_at'] = now
        industries_table.put_item(Item=event)
        
        return {
            'statusCode': 200,
            'body': "Industry added successfully"
        }
        
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
