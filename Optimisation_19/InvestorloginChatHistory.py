import json
import boto3

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define DynamoDB tables
investor = dynamodb.Table('InvestorLoginHistory')  # Table for investor login history
token_data = dynamodb.Table('Token')  # Table for token data
token_data_prod = dynamodb.Table('Token_Prod')  # Table for production token data

def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data tables.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found in any of the tables, False otherwise.
    """
    data = token_data.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        data = token_data_prod.get_item(Key={'token': token})
        if 'Item' in data:
            return True
        else:
            return False 

def lambda_handler(event, context):
    try:
        data = event

        # Check if required fields are present and not empty
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            # Token is valid, proceed with retrieving data
            data = investor.get_item(Key={'email': event['email'].lower(), 'time': event['time']})
            if 'Item' in data:
                return {
                    'statusCode': 200,
                    'body': data['Item']['data']
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
