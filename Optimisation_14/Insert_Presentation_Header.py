import json  # Library for JSON operations
import boto3  # AWS SDK for Python (Boto3)
from uuid import uuid4  # Library for generating UUIDs
from time import gmtime, strftime  # Library for time-related operations
from boto3.dynamodb.conditions import Key  # Conditions for DynamoDB queries

# Importing necessary libraries
dynamodb = boto3.resource('dynamodb')  # Initialize DynamoDB resource

# Get DynamoDB tables
user_table = dynamodb.Table('user')
presentation_table = dynamodb.Table('Presentation')
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the given token is valid.

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
    AWS Lambda handler function.

    Args:
        event (dict): The event data.
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response containing the status code and body.
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

        if token_checker(event['token']):
            unique_id = uuid4().hex
            presentation_dictionary = {}

            if event['email'] in ['admin@edyou.com', 'admin@edyou.in']:
                if event['tenantEmail'] == "":
                    event['email'] = ""
                else:
                    event['email'] = event['tenantEmail']

            presentation_dictionary['Tenantemail'] = event['email']

            if presentation_dictionary['Tenantemail'] != "":
                data = user_table.get_item(Key={'email': presentation_dictionary['Tenantemail'].lower()})
                if 'Item' in data:
                    presentation_dictionary['name'] = data['Item']['name']
            else:
                presentation_dictionary['name'] = ""

            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            presentation_dictionary['created_at'] = now
            presentation_dictionary['id'] = unique_id
            presentation_dictionary['title'] = event['title']
            presentation_dictionary['description'] = event['description']
            presentation_dictionary['URL'] = ""
            presentation_dictionary['Data'] = []
            presentation_dictionary['status'] = event['status']

            presentation_table.put_item(Item=presentation_dictionary)

            return {
                'statusCode': 200,
                'id': unique_id,
                'body': "Learning added successfully"
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid. Please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }