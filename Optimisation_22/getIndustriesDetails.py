import json  # Import the json module for JSON handling
import boto3  # Import the boto3 library for AWS service interactions
from uuid import uuid4  # Import the uuid4 function from the uuid module

# Create an instance of DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Industries' table
industries_table = dynamodb.Table('Industries')

# Get the 'Token' table
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the provided token is valid.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    return 'Item' in data
    # add
    # if true return true 
    # else false 

def lambda_handler(event, context):
    """
    AWS Lambda function entry point.

    Args:
        event (dict): The event data passed to the function.
        context (object): The runtime information of the function.

    Returns:
        dict: The response containing the status code and body.
    """
    try:
        # Extract data from the event
        data = event

        # Check for required fields in the data
        required_fields = ["token", "id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        # Check the validity of the token
        if token_checker(event['token']):
            # Get the item from the 'Industries' table
            data = industries_table.get_item(Key={'id': event['id']})
            if 'Item' in data:
                return {
                    'statusCode': 200,
                    'body': data['Item']
                }
            else:
                return {
                    'statusCode': 404,
                    'body': 'Item not found'
                    # replace the Item word with the meaningful word
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid. Please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
