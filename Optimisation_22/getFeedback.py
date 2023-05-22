import json  # Import the JSON module for handling JSON data
import boto3  # Import the Boto3 library for interacting with AWS services

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'feedback' and 'Token' tables
feedback_table = dynamodb.Table('feedback')
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Function to check if the provided token exists in the Token table.

    Parameters:
    - token (str): The token to check.

    Returns:
    - bool: True if the token exists, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False  

def lambda_handler(event, context):
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
            response = feedback_table.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = feedback_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            result.sort(key=lambda x: x['time'], reverse=True)
            return {
                'statusCode': 200,
                'body': result
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }
        
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
