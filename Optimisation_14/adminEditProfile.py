import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python

# Create a connection to DynamoDB service
dynamodb = boto3.resource('dynamodb')

# Access the 'user' table in DynamoDB
user_table = dynamodb.Table('user')

# Access the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid.

    Args:
        token (str): Token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    response = token_table.get_item(Key={'token': token})
    return 'Item' in response

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): Event data.
        context: Context data.

    Returns:
        dict: Response containing status code, body, and data.
    """
    try:
        data = event
        required_fields = ["email", "token", "f_name", "l_name", "contact"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            resp = user_table.get_item(Key={'email': event['email']})
            if "Item" in resp:
                item = resp['Item']
                item['email'] = event['email']
                item['name'] = event['f_name'] + " " + event['l_name']
                item['l_name'] = event['l_name']
                item['f_name'] = event['f_name']
                item['contact'] = event['contact']
                user_table.put_item(Item=item)

                return {
                    'statusCode': 200,
                    'body': 'Profile Updated',
                    'Data': item
                }
            else:
                return {
                    'statusCode': 404,
                    'body': 'User not found'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
