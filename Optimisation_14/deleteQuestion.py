import json
import boto3

# Create a DynamoDB resource object
dynamodb = boto3.resource('dynamodb')

# Get the 'Question' table from DynamoDB
question_table = dynamodb.Table('Question')

# Get the 'Token' table from DynamoDB
token_data_table = dynamodb.Table('Token')


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
    Lambda function handler to delete a question.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response containing the status code and body.
    """
    try:
        data = event
        required_fields = ["id", "token", "qid"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            questions = question_table.get_item(Key={'id': event['id']})
            if 'Item' in questions:
                stored_questions = questions['Item']['question']
                updated_questions = [i for i in stored_questions if not (i['qid'] == event['qid'])]
                questions['Item']['question'] = updated_questions
                question_table.put_item(Item=questions['Item'])

                return {
                    'statusCode': 200,
                    'body': 'Question deleted successfully'
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

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
