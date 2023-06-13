import json  # Import JSON module for handling JSON data
import boto3  # Import Boto3 library for interacting with AWS services
import requests  # Import Requests library for making HTTP requests

dynamodb = boto3.resource('dynamodb')  # Create a DynamoDB resource object
token_data_table = dynamodb.Table('Token')  # Get the Token table
investor_table = dynamodb.Table("Investor")  # Get the Investor table

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object provided by Lambda.

    Returns:
        dict: The response object.
    """
    print(event)

    # Get Investor data from the Investor table using email
    data = investor_table.get_item(Key={'email': event['email'].lower()})
    userData = data['Item']

    if 'prompt' not in userData:
        userData['prompt'] = "Hi " + userData['f_name'] + ", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"

    print(userData['prompt'])
    
    # Prepare custom and data payload
    custom = {
        "name": userData['name'],
        "email": userData['email'],
        "prompt": userData['prompt'],
        "time": userData['lastlogin'],
        "gptPrompt": userData['gptPrompt']
    }
    data = {
        "type": "QUESTION",
        "avatarSessionId": userData['sessionID']
    }

    # Prepare the request payload
    payload = {
        'sid': userData['token'],
        'fm-custom-data': json.dumps(custom),
        'fm-question': event['question'],
        'fm-avatar': json.dumps(data)
    }
    
    url = "https://v6w3mrkkya.execute-api.us-west-2.amazonaws.com/Development/UneeqAvatarforDev"

    headers = {
        'Content-Type': 'application/json'
    }
    
    # Make the HTTP POST request to the UneeqAvatarforDev API
    response1 = requests.post(url, headers=headers, data=json.dumps(payload))

    if response1.status_code == 200:
        print(response1.text)
        response = json.loads(response1.text)
        response = json.loads(response['answer'])
        print(response)

        if response['answer'] != '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">Getting response from OpenAI.</mstts:express-as></voice></speak>':
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/speakAPI"
            payload = json.dumps({
                "email": event["email"],
                "answer": response['answer'],
                "instructions": response['instructions']
            })
            print(payload)
            response = requests.post(url, headers=headers, data=payload)
            print(response.text)

            if response1.status_code == 200:
                return {
                    'statusCode': 200,
                    'body': "text"
                }
            else:
                return {
                    'statusCode': 200,
                    'body': "error"
                }
        else:
            return {
                'statusCode': 200,
                'body': "text"
            }
    else:
        return {
            'statusCode': 200,
            'body': "error"
        }
