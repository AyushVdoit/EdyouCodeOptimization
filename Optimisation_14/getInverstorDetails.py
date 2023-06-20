import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
investor_table = dynamodb.Table('Investor')
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
        required_fields = ["token"]

        # Check if required fields are present in the request data
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        # Check if token is valid
        if token_checker(event['token']):
            # Fetch data from the 'Investor' table based on email
            data = investor_table.get_item(Key={'email': event['email'].lower()})
            if 'Item' in data:
                return {
                    'statusCode': 200,
                    'body': data['Item']
                }
            else:
                return {
                    'statusCode': 404,
                    'body': 'No data found for the given email'
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
