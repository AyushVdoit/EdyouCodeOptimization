import json  # Import the JSON module for working with JSON data
import boto3  # Import the Boto3 library for interacting with AWS services
from uuid import uuid4  # Import the uuid4 function from the uuid module for generating UUIDs

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Websites' and 'Token' tables
websites_table = dynamodb.Table('Websites')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the given token is valid.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    """
    Lambda handler function.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response containing the statusCode and body.
    """
    if token_checker(event['token']):
        response = websites_table.scan()
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = websites_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        
        filtered_result = []
        for item in result:
            if item['type'] == "Dev":
                filtered_result.append(item)
        
        filtered_result.sort(key=lambda x: x['created_At'])
        
        return {
            'statusCode': 200,
            'body': filtered_result
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
