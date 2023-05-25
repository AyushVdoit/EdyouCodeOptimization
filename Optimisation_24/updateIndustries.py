import json  # For JSON serialization and deserialization
import boto3  # AWS SDK for Python
from uuid import uuid4  # For generating UUIDs


# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get reference to the 'industries_prod' table
industries_table = dynamodb.Table('Industries_Prod')

# Get reference to the 'token_prod' table
token_data_table = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Check if the token is valid.

    Args:
        token (str): The token to be checked.

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
    AWS Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response object containing the status code and body.
    """
    # Check token validity
    if token_checker(event['token']):
        # Remove token from the event data
        del event['token']
        
        # Add/update industry data in the 'Industries_Prod' table
        industries_table.put_item(Item=event)
        
        return {
            'statusCode': 200,
            'body': "Industry updated successfully"
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
