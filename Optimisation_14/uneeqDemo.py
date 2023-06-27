import jwt
import json
import requests


def lambda_handler(event, context):
    """
    Lambda function handler.
    
    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object provided by AWS Lambda.
        
    Returns:
        dict: The response from the API.
    """
    name = event['name'].split(" ")[0]
    email = event['email'].lower()
    
    tokens = event['token']
    jwt_secret = 'CF537D5E-A1AE-C1E1-1244-CA9B4856A127'  # Your JWT Secret
    
    custom_data = {"name": name, "email": email}
    api_url = 'https://api.us.uneeq.io'  # The correct regional endpoint for your account
    persona_id = '5c27bb2c-03e5-4f42-b984-c0549346567b'
    
    message = {
        'sid': tokens,
        'fm-workspace': persona_id,
        'fm-custom-data': json.dumps(custom_data, separators=(',', ':'), ensure_ascii=False)
    }
    
    compact_jws = jwt.encode(message, jwt_secret, algorithm='HS256')
    headers = {"Content-Type": "application/jwt", "workspace": persona_id}
    
    r = requests.post(api_url + "/api/v1/clients/access/tokens", data=compact_jws, headers=headers)
    response = r.json()
    
    return response
