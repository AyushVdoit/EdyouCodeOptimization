import json
import boto3

# Initializing DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing DynamoDB tables
topic_table = dynamodb.Table('Topic')
token_data_table = dynamodb.Table('Token')


def token_checker(token):
    """
    Checks if a token is valid by querying the Token table in DynamoDB.

    Args:
        token (str): The token to be checked.

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

        # Required fields in the event payload
        required_fields = ["Topic_id", "token", "topicName", "description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            result = topic_table.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in result:
                # Update the topic details
                topic_data = result['Item']
                topic_data['topicName'] = event['topicName']
                topic_data['industry'] = event['industry']
                topic_data['description'] = event['description']
                topic_data['status'] = event['status']
                topic_table.put_item(Item=topic_data)

            return {
                'statusCode': 200,
                'body': 'Topic updated successfully'
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
