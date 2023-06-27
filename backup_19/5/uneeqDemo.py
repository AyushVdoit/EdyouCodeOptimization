import jwt
import json
import requests
# import boto3
# dynamodb = boto3.resource('dynamodb')
# user=dynamodb.Table('user')


def lambda_handler(event, context):
    name = event['name'].split(" ")[0]
    # Data=user.get_item(Key={'email' : event['email'].lower()})
    email = event['email'].lower()
    
    tokens = event['token']
    jwt_secret = 'CF537D5E-A1AE-C1E1-1244-CA9B4856A127' # Your JWT Secret
    # gptPrompt=""
    # if 'Item' in Data:
    #     gptPrompt = Data['Item']['gptPromptUser']
    customData = {"name":name,"email":email}
    api_url = 'https://api.us.uneeq.io' # The correct regional endpoint for your account
    personaId = '5c27bb2c-03e5-4f42-b984-c0549346567b'
    # personaId = '61a3fa60-5008-4cff-8674-79ec9fd25b43'

    message = {
        # 'sid': '87e86c3c-6eb0-4a7a-99f2-cc046276196f', # Can be any value you wish0e177d80-2545-49f8-9d53-9a1070ce9835
        'sid':tokens,
        'fm-workspace': personaId,
        'fm-custom-data': json.dumps(customData, separators=(',', ':'), ensure_ascii=False) # You can simply `json.dumps({})` for simplicity
    }
    compact_jws = jwt.encode(message, jwt_secret, algorithm='HS256') # Algorithm is very importantly HS256, not RS256
    headers = {"Content-Type": "application/jwt", "workspace": personaId}
    r = requests.post(api_url + "/api/v1/clients/access/tokens", data=compact_jws, headers=headers)
    r = r.json()
    return r
    
