import json
import boto3
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')
Investor = dynamodb.Table("Investor")
def lambda_handler(event, context):
    print(event)
    Data=Investor.get_item(Key={'email' : event['email'].lower()})
    userData=Data['Item']
    if 'prompt' not in userData:
        userData['prompt']="Hi "+ userData['f_name']+", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"
    print(userData['prompt'])
    custom = {"name":userData['name'],"email":userData['email'],"prompt":userData['prompt'],"time":userData['lastlogin'],"gptPrompt":userData['gptPrompt']}
    data={"type":"QUESTION","avatarSessionId":userData['sessionID']}
    dici={'sid':userData['token'],'fm-custom-data':json.dumps(custom),
          'fm-question':event['question'],
          'fm-avatar':json.dumps(data)
          }
    url = "https://v6w3mrkkya.execute-api.us-west-2.amazonaws.com/Development/UneeqAvatarforDev"

    payload = json.dumps(dici)
    headers = {
      'Content-Type': 'application/json'
    }
    
    response1 = requests.request("POST", url, headers=headers, data=payload)
    if response1.status_code==200:
        print(response1.text) 
        response=json.loads(response1.text)
        response=json.loads(response['answer'])
        print(response)
        if response['answer']!='<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">Getting response from OpenAI.</mstts:express-as></voice></speak>':
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/speakAPI"
            payload = json.dumps({
              "email": event["email"],
              "answer": response['answer'],
              "instructions": response['instructions']
            })
            print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)  
            if response1.status_code==200:
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
    