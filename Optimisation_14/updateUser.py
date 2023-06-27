import json
import boto3

# Initializing DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing 'user_Prod' table
user_table = dynamodb.Table('user_Prod')

# Accessing 'Token_Prod' table
token_table = dynamodb.Table('Token_Prod')

def token_checker(token):
    """
    Checks if the provided token exists in the 'Token_Prod' table.

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
    if token_checker(event['token']):
        email = event['email'].lower()
        response = user_table.get_item(Key={'email': email})
        if 'Item' in response:
            del event['token']
            if event['gptPromptUser'] == "":
                event['gptPromptUser'] = "Everything"
            event['password'] = response['Item']['password']
            user_table.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "User updated successfully"
        }
