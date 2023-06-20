import json
import boto3

dynamodb = boto3.resource('dynamodb')
presentation_table = dynamodb.Table('Presentation')
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
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
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            presentation_details = presentation_table.get_item(Key={'id': event['id']})
            if 'Item' in presentation_details:
                return {
                    'statusCode': 200,
                    'body': presentation_details['Item']
                }
            else:
                return {
                    'statusCode': 200,
                    'body': "error no such file"
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
