import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
question_table = dynamodb.Table('Question_Prod')
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
        required_fields = ["id", "topic", "description", "max_marks", "series_title", "no_of_question"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if token_checker(event['token']):
            result = question_table.get_item(Key={'id': event['id']})
            
            if 'Item' in result:
                data = result['Item']
                data['topic'] = event['topic']
                data['description'] = event['description']
                data['max_marks'] = event['max_marks']
                data['series_title'] = event['series_title']
                data['no_of_question'] = event['no_of_question']
                
            question_table.put_item(Item=data)
            
            return {
                'statusCode': 200,
                'body': 'Test series updated successfully'
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }
        
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
