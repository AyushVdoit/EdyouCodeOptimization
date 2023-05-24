import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python

# Create an instance of DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'user', 'Industries', and 'Token' tables from DynamoDB
user_table = dynamodb.Table('user')
industries_table = dynamodb.Table('Industries')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response object.
    """
    if token_checker(event['token']):
        email = event['email'].lower()
        resp = user_table.get_item(Key={'email': email})
        if 'Item' in resp:
            del event['token']
            data = industries_table.get_item(Key={'id': event['industry']})
            if 'Item' in data:
                event['industryName'] = data['Item']['name']
            event['password'] = resp['Item']['password']
            
            user_table.put_item(Item=event)
        
        return {
            'statusCode': 200,
            'body': 'Tenant updated successfully'
        }
    # add else statement
    # return {
    #     'statusCode': 401,
    #     'body': 'Token is invalid, please re-login'
    # }
