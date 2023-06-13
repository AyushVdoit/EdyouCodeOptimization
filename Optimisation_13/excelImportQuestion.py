import json  # For working with JSON data
import secrets
import boto3  # AWS SDK for Python
from uuid import uuid4  # For generating UUIDs
from time import gmtime, strftime  # For working with time

from boto3.dynamodb.conditions import Key  # For querying DynamoDB

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# DynamoDB Tables
question_table = dynamodb.Table('Question')
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid.

    Args:
        token (str): The token to be checked.

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
    Lambda handler function.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response containing the status code and body.
    """
    if token_checker(event['token']):
        data = event['data']
        data_rows = data
        missing_fields_message = "The following fields are missing in column: "
        missing_fields = []
        count = 1

        for row in data_rows:
            count += 1
            required_fields = [
                "CorrectAnswer",
                "description__001",
                "description__002",
                "options__001",
                "options__002",
                "Question"
            ]
            field_names = {'Question': 'A','options__001': 'B','description__001': 'C',
            'options__002': 'D','description__002': 'E',
            'options__003': 'F','description__003': 'G','options__004': 'H',
            'description__004': 'I','options__005': 'J','description__005': 'K',
            'CorrectAnswer': 'L','hint': 'M'}

            for field in required_fields:
                if field not in row or not row[field]:
                    missing_fields.append(field_names[field] + str(count))

        if len(missing_fields) > 0:
            missing_fields_string = ', '.join(missing_fields)
            return {
                'statusCode': 400,
                'body': missing_fields_message + missing_fields_string
            }

        existing_question = question_table.get_item(Key={'id': event['id']})

        if 'Item' in existing_question:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            question_dictionary = existing_question['Item']
            questions = question_dictionary['question']

            for row in data:
                descriptions = []
                options = []
                for key in row:
                    if key.startswith("description__"):
                        descriptions.append(row[key])
                    elif key.startswith("options__"):
                        options.append(row[key])

                question = {}
                num_options = len(options)
                letters = [chr(i+65)+"." for i in range(num_options)]
                new_value = {i:f"Option {chr(i+65)}" for i in range(num_options)}
                replacements = {i: chr(i+65) for i in range(num_options)}
                new_options = []
                for i, option in enumerate(options):
                    new_option = f"{letters[i]} {option}"
                    new_options.append(new_option)
                lowercase_strings = [s.lower() for s in options]
                position = lowercase_strings.index(row['CorrectAnswer'].lower())

                question['correctAnswer'] = letters[position] + " " + options[position]
                question['correctPosition'] = position
                question['options'] = new_options

                if 'hint' in row:
                    question['hint'] = row['hint']
                else:
                    question['hint'] = ""

                for i, desc in enumerate(descriptions):
                    if i == position:
                        descriptions[i] = replacements[i] + " is correct because " + descriptions[i]
                    else:
                        descriptions[i] = replacements[i] + " is incorrect because " + descriptions[i]

                question['description'] = descriptions
                question['correctAnswerFrontend'] = new_value[position]
                question['created_at'] = now
                question['updated_at'] = now
                question['created_by'] = event["creator_name"]
                question['updated_by'] = event['creator_name']
                question["Question"] = row['Question']
                question['qid'] = uuid4().hex
                questions.append(question)
                question_dictionary['question'] = questions

            question_table.put_item(Item=question_dictionary)

            return {
                'statusCode': 200,
                'body': "File Uploaded Successfully"
            }
