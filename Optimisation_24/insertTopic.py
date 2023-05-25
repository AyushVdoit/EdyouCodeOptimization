import json  # For JSON serialization and deserialization
import boto3  # AWS SDK for Python
from uuid import uuid4  # For generating UUIDs
import secrets  # For generating secure random numbers
from boto3.dynamodb.conditions import Key  # For specifying conditions in DynamoDB queries
from time import gmtime, strftime  # For date and time manipulation
from datetime import timedelta, datetime  # For working with time intervals and dates
import string  # For working with strings
import random  # For generating random values
import smtplib  # For sending emails
import base64  # For base64 encoding and decoding

s3 = boto3.client('s3')  # AWS S3 client
dynamodb = boto3.resource('dynamodb')  # AWS DynamoDB resource
topic_table = dynamodb.Table('Topic')  # DynamoDB table for topics
token_table = dynamodb.Table('Token')  # DynamoDB table for tokens


def token_checker(token):
    """
    Checks the validity of a token in the Token table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False


def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: The response to return from the Lambda function.
    """
    try:
        data = event
        required_fields = ["Topic_id", "token", "correctAnswer", "Potential_Question"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            topic_data = topic_table.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in topic_data:
                topic_dictionary = topic_data['Item']
                topic_list = topic_dictionary['question']
                topic = {}
                for question in event["Potential_Question"]:
                    if question["subQ"] is not None:
                        pass
                    else:
                        return {
                            'statusCode': 400,
                            'body': 'Question variations are required and cannot be empty'
                        }
                uuid = uuid4().hex
                bucket_name = "pollydemo2022"
                object_key = 'images_dev/' + uuid + '.jpg'
                if event['imageUrl'] != "" and event['imageUrl'] is not None:
                    content_type = 'image/jpeg'
                    image_data = event['imageUrl'].replace("data:image/png;base64,", "")
                    image = base64.b64decode(image_data)
                    s3.put_object(Bucket=bucket_name, Key=object_key, Body=image, ContentType=content_type)
                    event['image'] = "https://pollydemo2022.s3.us-west-2.amazonaws.com/" + object_key
                    topic['image'] = event['image']
                    topic['imageUrl'] = event['image']
                else:
                    topic['image'] = ""
                    topic['imageUrl'] = ""

                if event['description'] != "" and event['description'] is not None:
                    if event['prompt_status'] == True or event['prompt_status'] is not None:
                        topic['description'] = event['description']
                    else:
                        topic['description'] = ""
                        event['prompt_status'] = False
                else:
                    topic['description'] = ""

                if event['url'] != "" and event['url'] is not None:
                    topic['url'] = event['url']
                    if event['followup'] != "" and event['followup'] is not None:
                        if event['followup_status']:
                            topic['followup'] = event['followup']
                        else:
                            topic['followup'] = "click me"
                    else:
                        topic['followup'] = "click me"
                else:
                    topic['url'] = ""
                    topic['followup'] = ""

                topic['correctAnswer'] = (
                    event['correctAnswer']
                    + "7481903939urlforyou="
                    + topic['url']
                    + "7581903939imagelinkforyou="
                    + topic['image']
                    + "7581904949Textlinkforyou="
                    + topic['description']
                    + "7581904949Followup="
                    + topic['followup']
                )
                topic['followup_status'] = event['followup_status']
                topic["Potential_Question"] = event['Potential_Question']
                topic['qid'] = uuid
                topic['description'] = topic['description']
                topic['prompt_status'] = event['prompt_status']
                topic_list.append(topic)
                topic_dictionary['question'] = topic_list
                topic_table.put_item(Item=topic_dictionary)
                return {
                    'statusCode': 200,
                    'body': "Question added successfully"
                }
            else:
                return {
                    'statusCode': 200,
                    'body': 'No data found'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid. Please re-login'
            }

    except (
        TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError
    ) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
