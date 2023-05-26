import boto3  # AWS SDK library for interacting with AWS services
import json  # Library for working with JSON data
import jwt  # Library for encoding and decoding JSON Web Tokens (JWT)
import os  # Library for interacting with the operating system
import requests  # Library for making HTTP requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB table
token_data = dynamodb.Table('Token')


def lambda_handler(event, context):
    """
    Lambda handler function to process and generate an avatar speak response.

    Parameters:
    - event: The event data passed to the Lambda function.
    - context: The runtime information of the Lambda function.

    Returns:
    - The content of the HTTP response from the avatar speak API.
    """

    print(event)
    session_id_jwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    session_id = event['sessionId']
    rules = event['rules']
    headers = {
        "Content-Type": 'application/json'
    }

    encoded_session_id_jwt = jwt.encode({'sessionId': f'{session_id}'}, session_id_jwt, algorithm='HS256')

    instructions = {
        "instructions": {
            "uneeqData": {
                "emotion": {
                    "fear": "strong"
                }
            }
        }
    }

    body = {
        'answer': rules,
        'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
        'sessionIdJwt': encoded_session_id_jwt
    }
    
    url = "https://api.us.uneeq.io/api/v1/avatar/" + session_id + "/speak"
    response = requests.post(url, data=json.dumps(body), headers=headers)
    print(response)

    return response.content
