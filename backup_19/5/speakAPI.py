import boto3
import json
import jwt
import os
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')
Investor = dynamodb.Table("Investor")

def lambda_handler(event, context):
    print(event)
    Data=Investor.get_item(Key={'email' : event['email'].lower()})
    userData=Data['Item']

    
    sessionIdJwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    sessionId = userData['sessionID']
    headers = {
      "Content-Type": 'application/json'
    }
    instructions={"instructions":event['instructions']}
    encodedSessionIdJwt = jwt.encode({'sessionId': f'{sessionId}'}, sessionIdJwt, algorithm='HS256')
    body = {
      'answer': event['answer'],
      # 'answer':Qdata,
      'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
      'sessionIdJwt': encodedSessionIdJwt
    }
    print(body)
    url = "https://api.us.uneeq.io/api/v1/avatar/"+sessionId+"/speak"
    response = requests.post(url, data = json.dumps(body), headers = headers)
    status_code = response.status_code
    print(response.status_code)
    print(response.content)
    return response.content

