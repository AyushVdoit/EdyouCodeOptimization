import json
import boto3
from boto3.dynamodb.conditions import Key

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define DynamoDB tables
topic = dynamodb.Table('Topic')
token_data = dynamodb.Table('Token')


def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found, False otherwise.
    """
    data = token_data.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False


def lambda_handler(event, context):
    try:
        data = event

        # Check if required fields are present and not empty
        required_fields = ["token", "Topic_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            data2 = topic.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in data2:
                size = len(data2['Item']['question'])
                l = []
                for i in data2['Item']['question']:
                    string = i['correctAnswer']
                    i['correctAnswer'] = string.split("7481903939")[0]
                    l.append(i)
                if size > 0:
                    return {
                        'statusCode': 200,
                        'body': l
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
                'body': 'Token is invalid. Please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
