import json  # JSON manipulation
import boto3  # AWS SDK for Python

dynamodb = boto3.resource('dynamodb')  # DynamoDB resource
question_table = dynamodb.Table('Question')  # Question table in DynamoDB
token_data_table = dynamodb.Table('Token')  # Token Data table in DynamoDB

def token_checker(token):
    """
    Check if the token is valid by looking it up in the Token Data table.

    Args:
        token (str): Token string to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): Event data passed to the function.
        context (object): Runtime information of the function.

    Returns:
        dict: The response object containing the HTTP status code and body.
    """
    try:
        data = event
        required_fields = ["id"]
        # Check if required fields are present
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            if event['status'] == 'Inactive':
                for id in event['id']:
                    question_info = question_table.get_item(Key={'id': id})
                    question_info['Item']['status'] = event['status']
                    question_table.put_item(Item=question_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Test series deactivated successfully.'
                }
            elif event['status'] == 'Active':
                for id in event['id']:
                    question_info = question_table.get_item(Key={'id': id})
                    question_info['Item']['status'] = event['status']
                    question_table.put_item(Item=question_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Test series activated successfully.'
                }
            elif event['status'] == 'Delete':
                for id in event['id']:
                    question_info = question_table.get_item(Key={'id': id})
                    question_info['Item']['status'] = event['status']
                    question_table.put_item(Item=question_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Test series deleted successfully.'
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Error'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (
            TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
