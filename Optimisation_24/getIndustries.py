import json  # Library for working with JSON data
import boto3  # AWS SDK for Python
from uuid import uuid4  # Library for generating UUIDs

dynamodb = boto3.resource('dynamodb')  # Amazon DynamoDB resource for working with DynamoDB tables
industries_table = dynamodb.Table('Industries')  # DynamoDB table for storing industries data
token_table = dynamodb.Table('Token')  # DynamoDB table for storing token data


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
        response = industries_table.scan()
        result = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = industries_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        
        result.sort(key=lambda x: x['created_at'], reverse=False)
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
