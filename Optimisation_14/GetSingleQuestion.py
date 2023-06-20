import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
question_table = dynamodb.Table('Question')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda handler function to handle the AWS Lambda event.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object representing the runtime information.

    Returns:
        dict: The response containing the HTTP status code and body.
    """
    try:
        data = event
        required_fields = ["token", "id"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if token_checker(event['token']):
            data2 = question_table.get_item(Key={'id': event['id']})
            if 'Item' in data2:
                questions = data2['Item'].get('question', [])
                for question in questions:
                    if question['qid'] == event['qid']:
                        break
                else:
                    question = None
                
                if question:
                    question['correctAnswer'] = question['correctAnswer'][3:]
                    for i in range(len(question['description'])):
                        if i != question['correctPostioin']:
                            question['description'][i] = question['description'][i][2:]
                            question['description'][i] = question['description'][i].replace("is incorrect because ", "")
                        else:
                            question['description'][i] = question['description'][i][2:]
                            question['description'][i] = question['description'][i].replace("is correct because ", "")
                
                    for i in range(len(question['options'])):
                        question['options'][i] = question['options'][i][3:]
                    
                    return {
                        'statusCode': 200,
                        'body': question
                    }
                else:
                    return {
                        'statusCode': 404,
                        'body': 'Question not found'
                    }
            else:
                return {
                    'statusCode': 400,
                    'body': 'No data found'
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
