import json  # JSON manipulation
import boto3  # AWS SDK for Python

dynamodb = boto3.resource('dynamodb')  # DynamoDB resource
topic_table = dynamodb.Table('Topic')  # Topic table in DynamoDB
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
            if event['status'] == 'Inactive':
                for id in event['Topic_id']:
                    topic_info = topic_table.get_item(Key={'Topic_id': id})
                    topic_info['Item']['status'] = event['status']
                    topic_table.put_item(Item=topic_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Topic deactivated successfully'
                }
            elif event['status'] == 'Active':
                for id in event['Topic_id']:
                    topic_info = topic_table.get_item(Key={'Topic_id': id})
                    topic_info['Item']['status'] = event['status']
                    topic_table.put_item(Item=topic_info['Item'])
                return {
                    'statusCode': 200,
                    'body': f'Topic activated successfully'
                }
            elif event['status'] == 'Delete':
                for id in event['Topic_id']:
                    topic_info = topic_table.get_item(Key={'Topic_id': id})
                    topic_info['Item']['status'] = event['status']
                    topic_table.put_item(Item=topic_info['Item'])
                return {
                    'statusCode': 200,
                    'body': f'Topic deleted successfully'
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Error'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }

    except (
            TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
