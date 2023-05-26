# JSON library for working with JSON data
import json

# Boto3 library for interacting with AWS services
import boto3

# UUID library for generating unique IDs
from uuid import uuid4

# Time library for working with timestamps
from time import gmtime, strftime

# Boto3 DynamoDB conditions for query and scan operations
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
question_table = dynamodb.Table('Question_Prod')
user_table = dynamodb.Table('user_Prod')
token_data_table = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Check if the provided token is valid.

    Args:
        token (str): The token to check.

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
    Lambda function entry point.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Lambda function context.

    Returns:
        dict: Response containing the status code and body.
    """
    try:
        data = event
        required_fields = ["token", "description", "max_marks", "series_title", "no_of_question"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            unique_id = uuid4().hex
            question_dictionary = {}

            if event['email'] in ['admin@edyou.com', 'admin@edyou.in']:
                if event['tenantEmail'] == "" or event['tenantEmail'] == "none":
                    event['email'] = ""
                else:
                    event['email'] = event['tenantEmail']
            
            question_dictionary['Tenantemail'] = event['email']
            
            if question_dictionary['Tenantemail'] != "":
                data = user_table.get_item(Key={'email': question_dictionary['Tenantemail'].lower()})
                if 'Item' in data:
                    question_dictionary['name'] = data['Item']['name']
            else:
                question_dictionary['name'] = ""
            
            question_dictionary['id'] = unique_id
            question_dictionary['topic'] = event['topic']
            question_dictionary['question'] = []
            question_dictionary['description'] = event['description']
            question_dictionary['max_marks'] = event['max_marks']
            question_dictionary['no_of_question'] = event['no_of_question']
            question_dictionary['series_title'] = event['series_title']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            question_dictionary['created_at'] = now
            question_dictionary['status'] = event['status']
            
            question_table.put_item(Item=question_dictionary) 
            
            return {
                'statusCode': 200,
                'id': unique_id,
                'body': "Test series added successfully"
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
