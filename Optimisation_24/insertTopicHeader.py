import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
from uuid import uuid4  # Library for generating UUIDs
from boto3.dynamodb.conditions import Key  # Condition expression helper for DynamoDB queries
from time import gmtime, strftime  # Library for working with time

# Initializing the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing the 'user' table in DynamoDB
user_table = dynamodb.Table('user')

# Accessing the 'Topic' table in DynamoDB
topic_table = dynamodb.Table('Topic')

# Accessing the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

# Function to check the validity of a token in the Token table
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

# AWS Lambda function handler
def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Context object representing the runtime information.

    Returns:
        dict: Response data to be returned by the Lambda function.
    """
    try:
        data = event
        required_fields = ["token", "topicName", "description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if token_checker(event['token']):
            unique_id = uuid4().hex
            topic_dictionary = {}
            
            if event['email'] in ['admin@edyou.com', 'admin@edyou.in']:
                if event['tenantEmail'] == "":
                    event['email'] = ""
                else:
                    event['email'] = event['tenantEmail']
            
            topic_dictionary['Tenantemail'] = event['email']
            
            if topic_dictionary['Tenantemail'] != "":
                data = user_table.get_item(Key={'email': topic_dictionary['Tenantemail'].lower()})
                if 'Item' in data:
                    topic_dictionary['name'] = data['Item']['name']
            else:
                topic_dictionary['name'] = ""
            
            topic_dictionary['Topic_id'] = unique_id
            topic_dictionary['topicName'] = event['topicName']
            topic_dictionary['question'] = []
            topic_dictionary['industry'] = event['industry']
            topic_dictionary['description'] = event['description']
            topic_dictionary['status'] = event['status']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            topic_dictionary['created_at'] = now
            topic_table.put_item(Item=topic_dictionary) 
            
            return {
                'statusCode': 200,
                'id': unique_id,
                'body': "Topic added successfully"
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
