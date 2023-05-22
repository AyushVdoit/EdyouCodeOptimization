import boto3  # Import the Boto3 library for interacting with AWS services
import json  # Import the JSON module for handling JSON data
import jwt  # Import the JWT library for encoding and decoding JWTs
import os  # Import the OS module for operating system functionalities
import requests  # Import the Requests library for making HTTP requests

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Token' and 'Investor' tables
token_table = dynamodb.Table('Token')
investor_table = dynamodb.Table('Investor')

def lambda_handler(event, context):
    print(event)
    # Get user data from the 'Investor' table based on the email
    data = investor_table.get_item(Key={'email': event['email'].lower()})
    user_data = data['Item']

    # Define the sessionIdJwt, sessionId, headers, and instructions
    sessionIdJwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    sessionId = user_data['sessionID']
    headers = {
        "Content-Type": 'application/json'
    }
    instructions = {"instructions": event['instructions']}
    
    # Encode the sessionIdJwt and create the request body
    encodedSessionIdJwt = jwt.encode({'sessionId': f'{sessionId}'}, sessionIdJwt, algorithm='HS256')
    body = {
        'answer': event['answer'],
        'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
        'sessionIdJwt': encodedSessionIdJwt
    }
    
    print(body)
    
    # Send the POST request to the UneeQ API
    url = "https://api.us.uneeq.io/api/v1/avatar/" + sessionId + "/speak"
    response = requests.post(url, data=json.dumps(body), headers=headers)
    status_code = response.status_code
    
    print(response.status_code)
    print(response.content)
    
    return response.content
