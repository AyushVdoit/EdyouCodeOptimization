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
        required_fields = ["Topic_id", "token", "qid"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            # Fetch topic info with matching topic id
            topic_info = topic_table.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in topic_info:
                question = topic_info['Item']['question']
                updated_questions = [i for i in question if not (i['qid'] == event['qid'])]
                topic_info['Item']['question'] = updated_questions
                topic_table.put_item(Item=topic_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Topic deleted successfully'
                }
            else:
                return {
                    'statusCode': 200,
                    'body': 'No item found'
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
