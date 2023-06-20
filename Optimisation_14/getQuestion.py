import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
question_table = dynamodb.Table('Question')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda handler function to handle the AWS Lambda event.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object representing the runtime information.

    Returns:
        dict: The response containing the HTTP status code and body.
    """
    try:
        data = event
        required_fields = ["token", "id"]

        # Check if required fields are present in the request data
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        # Check if token is valid
        if token_checker(event['token']):
            data2 = question_table.get_item(Key={'id': event['id']})
            if 'Item' in data2:
                question_list = len(data2['Item']['question'])
                if question_list > 0:
                    return {
                        'statusCode': 200,
                        'body': data2['Item']['question']
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No questions are added yet"
                    }
            else:
                return {
                    'statusCode': 400,
                    'body': 'No data found'
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
