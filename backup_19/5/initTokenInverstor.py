import jwt
import json
import requests
import boto3
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')


def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["name","email","token","lastlogin"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: required and cannot be empty'
                }
        name = event['name'].split(" ")[0]
        # prompt = event['prompt']
        email = event['email']
        tokens = event['token']
        time = event['lastlogin']
        jwt_secret = 'CF537D5E-A1AE-C1E1-1244-CA9B4856A127' # Your JWT Secret
        Data=Investor.get_item(Key={'email' : event['email'].lower()})
        gptPrompt=""
        if 'Item' in Data:
            if Data['Item']['prompt_status'] ==True:
                if 'prompt' in Data['Item']:
                    prompt=Data['Item']['prompt']
                else:
                    prompt = "Hi "+ name+", welcome to the world of edYOU. I am Hannah. How can I help you?"

            else:
                prompt = "Hi "+ name+", welcome to the world of edYOU. I am Hannah. How can I help you?"
            gptPrompt = Data['Item']['gptPrompt']    
        customData = {"name":name,"email":email,"prompt":prompt,"time":time,"gptPrompt":gptPrompt}
        api_url = 'https://api.us.uneeq.io' # The correct regional endpoint for your account
        personaId= "e8b92f57-d619-4090-9450-4b47a0e375a5"
        message = {
            # 'sid': '87e86c3c-6eb0-4a7a-99f2-cc046276196f', # Can be any value you wish0e177d80-2545-49f8-9d53-9a1070ce9835
            'sid':tokens,
            # 'fm-workspace': '5c27bb2c-03e5-4f42-b984-c0549346567b',
            'fm-workspace':"e8b92f57-d619-4090-9450-4b47a0e375a5",
            'fm-custom-data': json.dumps(customData, separators=(',', ':'), ensure_ascii=False) # You can simply `json.dumps({})` for simplicity
        }
        compact_jws = jwt.encode(message, jwt_secret, algorithm='HS256') # Algorithm is very importantly HS256, not RS256
        headers = {"Content-Type": "application/jwt", "workspace": personaId}
        r = requests.post(api_url + "/api/v1/clients/access/tokens", data=compact_jws, headers=headers)
        r = r.json()
        Data['Item']['firstTime']=False
        Investor.put_item(Item=Data['Item'])
        print(r)
        return {
            'token':r['token'],
            'statusCode':200}
        # return customData
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
        return {
            'statusCode': 400,
            'body': f'Error: required and cannot be empty'
        }