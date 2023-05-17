import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
topic = dynamodb.Table('Topic')
token_data = dynamodb.Table('Token')


def token_checker(token):
    data = token_data.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

# to get topic info with given input topic id


def lambda_handler(event, context):
    try:

        data = event
        required_fields = ["token", "Topic_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            topic_info = topic.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in topic_info:
                size = len(topic_info['Item']['question'])
                topics = []
                for topic_question in topic_info['Item']['question']:
                    correct_answer = topic_question['correctAnswer']
                    topic_question['correctAnswer'] = correct_answer.split("7481903939")[
                        0]
                    topics.append(topic_question)
                if size > 0:
                    return {
                        'statusCode': 200,
                        'body': topics
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No question is added yet"
                    }
            else:
                return {
                    'statusCode': 400,
                    'body': 'No data found'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
