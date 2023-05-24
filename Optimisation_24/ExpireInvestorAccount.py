import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python

# Create an instance of DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Investor' and 'Token' tables from DynamoDB
investor_table = dynamodb.Table('Investor')
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        data = token_table.get_item(Key={'token': token})
        if 'Item' in data:
            return True
        else:
            return False 

def lambda_handler(event, context):
    if token_checker(event['token']):
        # Update the 'Investor' table to set the expiredPassword and expire_time attributes
        investor_table.update_item(
            Key={
                'email': event['email'].lower(),
            },
            UpdateExpression="set expired_password = :g, expire_time = :h",
            ExpressionAttributeValues={
                ':g': True,
                ':h': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': 'Account Expired'
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid, please re-login'
        }
