import boto3
import json
import jwt
import os
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')

def lambda_handler(event, context):
    print(event)
    sessionIdJwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    sessionId = event['sessionId']
    # s = ''.join(event['rules'].splitlines())
    # rules ='<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+ event['rules']+'</mstts:express-as></voice></speak>'
    rules = event['rules']
    headers = {
      "Content-Type": 'application/json'
    }
    
    encodedSessionIdJwt = jwt.encode({'sessionId': f'{sessionId}'}, sessionIdJwt, algorithm='HS256')
    
    instructions = {
      "instructions":{
      "uneeqData": {
      "emotion": {
        "fear": "strong"
      }}
      }
    }
    # rules="<uneeq:camera_face />"+rules
    # rules = "<uneeq:emotion_joy_normal />"+rules
    # rules = "<uneeq:emotion_fear_strong />"+rules
    body = {
      'answer':rules,
      'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
      'sessionIdJwt': encodedSessionIdJwt
    }
    url = "https://api.us.uneeq.io/api/v1/avatar/"+sessionId+"/speak"
    response = requests.post(url, data = json.dumps(body), headers = headers)
    print(response)
    return response.content
