import json  # Import JSON module for handling JSON data
import boto3  # Import Boto3 library for interacting with AWS services
from uuid import uuid4  # Import uuid4 from uuid module for generating UUIDs
from time import gmtime, strftime  # Import gmtime and strftime from time module for time-related operations
from boto3.dynamodb.conditions import Key  # Import Key from boto3.dynamodb.conditions module
dynamodb = boto3.resource('dynamodb')  # Create a DynamoDB resource object
user_table = dynamodb.Table('user')  # Get the user table
presentation_table = dynamodb.Table('Presentation')  # Get the presentation table
token_table = dynamodb.Table('Token')  # Get the token table

def TokenChecker(token):
    """
    Check if the token exists in the token table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object provided by Lambda.

    Returns:
        dict: The response object.
    """
    try:
        data = event
        required_fields = ["token", "title"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if TokenChecker(event['token']):
            result = presentation_table.get_item(Key={'id': event['id']})
            if 'Item' in result:
                presentation_dictionary = result['Item']
                presentation_dictionary['title'] = event['title']
                presentation_dictionary['description'] = event['description']
                presentation_table.put_item(Item=presentation_dictionary)
                return {
                    'statusCode': 200,
                    'body': "Learning updated successfully"
                }
            else:
                return {
                    'statusCode': 200,
                    'body': "E"
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
