import json
import boto3

dynamodb = boto3.resource('dynamodb')  # Amazon DynamoDB resource for working with DynamoDB tables
user_table = dynamodb.Table('user')  # DynamoDB table for storing user data
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
            data = user_table.get_item(Key={'email': event['email'].lower()})
            if 'Item' in data:
                return {
                    'statusCode': 200,
                    'body': data['Item']
                }
            # remove the comment if else part is require
            # else:
            #     return {
            #         'statusCode': 200,
            #         'body': 'User not found'
            #     }
            
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
