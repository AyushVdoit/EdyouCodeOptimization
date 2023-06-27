import json
import boto3
from time import sleep

# Initializing DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing 'Presentation' table
presentation_table = dynamodb.Table('Presentation')

# Accessing 'Token' table
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the provided token exists in the 'Token' table.

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
    AWS Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response with status code and body message.
    """
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
            presentation_details = presentation_table.get_item(Key={'id': event['id']})
            if 'Item' in presentation_details:
                presentation_details['Item']["URL"] = event["URL"]
                presentation_details['Item']["Data"] = []
                presentation_table.put_item(Item=presentation_details['Item'])
                sleep(7)  # Added a delay of 7 seconds (you can adjust the sleep time as needed)
                return {
                    'statusCode': 200,
                    'body': "Presentation updated."
                }
            else:
                return {
                    'statusCode': 200,
                    'body': "Error: No such file."
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
