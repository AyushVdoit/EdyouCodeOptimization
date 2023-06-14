import json
import boto3
from uuid import uuid4
import secrets
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
import string
import random
import smtplib

# Creating DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing the Question table in DynamoDB
question_table = dynamodb.Table('Question')
# Accessing the Token table in DynamoDB
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the provided token is valid.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    # Retrieve the token data from the Token table
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: The response containing the status code and body.
    """
    data = event
    required_fields = ["id", "token", "Question", "correctAnswer", "description", "options"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
            }

    if token_checker(event['token']):
        data2 = question_table.get_item(Key={'id': event['id']})
        if 'Item' in data2:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            question_dictionary = data2['Item']
            question1 = question_dictionary['question']
            question = {}
            options = event['options']
            options = [item for item in options if item is not None and item != ""]

            length1 = len(options)
            letters = [chr(i + 65) + "." for i in range(length1)]
            new_value = {f"Option {chr(i + 65)}": i for i in range(length1)}
            replacements = {i: chr(i + 65) for i in range(length1)}

            new_options = []
            for i, option in enumerate(options):
                new_option = f"{letters[i]} {option}"
                new_options.append(new_option)

            position = new_value[event['correctAnswer']]
            question['correctAnswer'] = f"{letters[position]} {options[position]}"
            question['correctPostion'] = position
            question['correctAnswerFrontend'] = event['correctAnswer']
            question["options"] = new_options

            if 'hint' in event:
                question['hint'] = event['hint']
            else:
                question['hint'] = ""

            description = event['description']
            description = [item for item in description if item is not None and item != ""]

            for i, desc in enumerate(description):
                if i == position:
                    description[i] = f"{replacements[i]} is correct because {description[i]}"
                else:
                    description[i] = f"{replacements[i]} is incorrect because {description[i]}"

            question['description'] = description
            question["Question"] = event['Question']
            question['qid'] = uuid4().hex
            question['hint'] = event['hint']
            question['created_at'] = now
            question['updated_at'] = now
            question['created_by'] = event['creator_name']
            question['updated_by'] = event['creator_name']

            question1.append(question)
            question_dictionary['question'] = question1
            question_table.put_item(Item=question_dictionary)

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
            'body': 'Token is invalid, please re-login'
        }
