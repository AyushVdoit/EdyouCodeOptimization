import boto3
import json
import jwt
import os
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')

def lambda_handler(event, context):
    session_id_jwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    session_id = event['sessionId']
    message = event['message']
    headers = {
      "Content-Type": 'application/json'
    }
    # rule1 = rules.replace("e-dee-you","EDU")
    encoded_session_id_jwt = jwt.encode({'sessionId': f'{session_id}'}, session_id_jwt, algorithm='HS256')
    instruction = {
            "customData": {'Question':"",
            "options":[],
            "text":message,
            "Output":message,
            "link":"",
            "imageUrl":"",
            "Test":"",
            "description":"",
            "followup":""
        }
    }
    instructions={"instructions":instruction}
    answer_data = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+message+'</mstts:express-as></voice></speak>'    
      
    body = {
      'answer': answer_data,
      'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
      'sessionIdJwt': encoded_session_id_jwt
    }
    url = "https://api.us.uneeq.io/api/v1/avatar/"+session_id+"/speak"
    response = requests.post(url, data = json.dumps(body), headers = headers)
    
    return response.content
