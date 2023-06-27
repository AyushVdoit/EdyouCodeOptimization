import json
import boto3
from time import gmtime, strftime
from uuid import uuid4

# Initializing DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing 'Question' table
question_table = dynamodb.Table('Question')

# Accessing 'Token' table
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token exists, False otherwise.
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
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response with status code and body message.
    """
    data = event
    required_fields = ["id", "token", "qid", "correctAnswer", "description", "options", "Question"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
            }

    if token_checker(event['token']):
        response = question_table.get_item(Key={'id': event["id"]})
        if 'Item' in response:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            question_dictionary = response['Item']
            question_list = question_dictionary['question']
            question = {}
            question['qid'] = event['qid']
            options = [item for item in event['options'] if item is not None and item != ""]
            length = len(options)
            letters = [chr(i+65)+"." for i in range(length)]
            new_value = {f"Option {chr(i+65)}": i for i in range(length)}
            replacements = {i: chr(i+65) for i in range(length)}

            new_options = [f"{letters[i]} {option}" for i, option in enumerate(options)]
            position = new_value[event['correctAnswer']]
            question['correctAnswer'] = f"{letters[position]} {options[position]}"
            question['correctPosition'] = position
            question['correctAnswerFrontend'] = event['correctAnswer']
            question["options"] = new_options

            description = [item for item in event['description'] if item is not None and item != ""]
            if 'hint' in event:
                question['hint'] = event['hint']
            else:
                question['hint'] = ""

            for i, desc in enumerate(description):
                if i == position:
                    description[i] = f"{replacements[i]} is correct because {description[i]}"
                else:
                    description[i] = f"{replacements[i]} is incorrect because {description[i]}"

            question['description'] = description
            question["Question"] = event['Question']
            question['updated_at'] = now
            question['updated_by'] = event['creator_name']
            question['created_at'] = now
            question['created_by'] = ""

            index = next((i for i, q in enumerate(question_list) if q['qid'] == event['qid']), None)
            if index is not None:
                question_list[index] = question
                question_dictionary['question'] = question_list
                question_table.put_item(Item=question_dictionary)
                return {
                    'statusCode': 200,
                    'body': "Question updated successfully"
                }
            else:
                return {
                    'statusCode': 200,
                    'body': 'No item Found'
                }

        else:
            return {
                'statusCode': 200,
                'body': 'No item Found'
            }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
