import json  # Import JSON module for handling JSON data
import boto3  # Import Boto3 library for interacting with AWS services

dynamodb = boto3.resource('dynamodb')  # Create a DynamoDB resource object
industries_table = dynamodb.Table('Industries')  # Get the Industries table
token_data_table = dynamodb.Table('Token')  # Get the Token table

def token_checker(token):
    """
    Check if the provided token is valid.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})  # Get the token item from Token table
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
        required_fields = ["token", "id"]

        # Check if required fields are present
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            # Delete industry item from the Industries table
            response = industries_table.delete_item(Key={'id': event['id']})

            return {
                'statusCode': 200,
                'body': 'Industry deleted successfully'
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }