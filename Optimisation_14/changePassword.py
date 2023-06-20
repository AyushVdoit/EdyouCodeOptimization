import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
from boto3.dynamodb.conditions import Key  # Library for working with DynamoDB conditions
from werkzeug.security import check_password_hash, generate_password_hash  # Library for password hashing

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
        dict: Response containing status code and body.
    """
    try:
        data = event
        required_fields = ["email", "token", "password", "confpassword", "oldpassword"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            email = event['email'].lower()
            data2 = user_table.get_item(Key={'email': email})
            if 'Item' in data2:
                if check_password_hash(data2['Item']['password'], event['oldpassword']):
                    if event['password'] == event['confpassword']:
                        hashed_password = generate_password_hash(event['confpassword'], method='sha256')
                        data2['Item']['password'] = hashed_password
                        user_table.put_item(Item=data2['Item'])
                        return {
                            'statusCode': 200,
                            'body': 'Password Updated'
                        }
                    else:
                        return {
                            'statusCode': 400,
                            'body': "Password didn't match"
                        }
                else:
                    return {
                        'statusCode': 400,
                        'body': "Password didn't match with the old password"
                    }
            else:
                return {
                    'statusCode': 400,
                    'body': 'No user found'
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
