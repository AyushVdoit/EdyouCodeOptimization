# Import the required libraries
import jwt  # Library for encoding and decoding JSON Web Tokens (JWT)
import json  # Library for working with JSON data
import requests  # Library for making HTTP requests
import boto3  # AWS SDK library for interacting with AWS services

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB table
investor_table = dynamodb.Table('Investor')


def lambda_handler(event, context):
    """
    Lambda handler function to generate an access token for the edYOU API.

    Parameters:
    - event: The event data passed to the Lambda function.
    - context: The runtime information of the Lambda function.

    Returns:
    - A dictionary containing the generated token and the HTTP status code.
    """

    try:
        data = event
        required_fields = ["name", "email", "token", "lastlogin"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': 'Error: required and cannot be empty'
                }

        # Extract data from the event
        name = event['name'].split(" ")[0]
        email = event['email']
        tokens = event['token']
        time = event['lastlogin']
        jwt_secret = 'CF537D5E-A1AE-C1E1-1244-CA9B4856A127'  # Your JWT Secret

        # Get data from the Investor table
        data = investor_table.get_item(Key={'email': event['email'].lower()})
        gptPrompt = ""
        if 'Item' in data:
            if data['Item']['prompt_status'] == True:
                if 'prompt' in data['Item']:
                    prompt = data['Item']['prompt']
                else:
                    prompt = "Hi " + name + ", welcome to the world of edYOU. I am Hannah. How can I help you?"
            else:
                prompt = "Hi " + name + ", welcome to the world of edYOU. I am Hannah. How can I help you?"
            gptPrompt = data['Item']['gptPrompt']

        customData = {"name": name, "email": email, "prompt": prompt, "time": time, "gptPrompt": gptPrompt}
        api_url = 'https://api.us.uneeq.io'  # The correct regional endpoint for your account
        personaId = "e8b92f57-d619-4090-9450-4b47a0e375a5"
        message = {
            'sid': tokens,
            'fm-workspace': personaId,
            'fm-custom-data': json.dumps(customData, separators=(',', ':'), ensure_ascii=False)
        }
        compact_jws = jwt.encode(message, jwt_secret, algorithm='HS256')
        headers = {"Content-Type": "application/jwt", "workspace": personaId}
        r = requests.post(api_url + "/api/v1/clients/access/tokens", data=compact_jws, headers=headers)
        r = r.json()

        # Update the firstTime flag in the Investor table
        data['Item']['firstTime'] = False
        investor_table.put_item(Item=data['Item'])

        return {
            'token': r['token'],
            'statusCode': 200
        }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': 'Error: required and cannot be empty'
        }
