import boto3
import json
import jwt
import os
import requests
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')
def lambda_handler(event, context):
    sessionIdJwt = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    sessionId = event['sessionId']
    token = event['token']
    Qdata = event['Qdata']
    Current = event['Current']
    if type(Qdata) ==type(token):
        headers = {
          "Content-Type": 'application/json'
        }
        encodedSessionIdJwt = jwt.encode({'sessionId': f'{sessionId}'}, sessionIdJwt, algorithm='HS256')
        
        instruction = {
                "customData": {'Question':"",
                "options":[],   
                "Output":Qdata,
                "Test":"",
                "text":Qdata,
                "link":"",
                "imageUrl":""
              }
        }
        instructions={"instructions":instruction}
        data4 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+Qdata+'</mstts:express-as></voice></speak>'    
        
        body = {
          'answer': data4,
          # 'answer':Qdata,
          'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
          'sessionIdJwt': encodedSessionIdJwt
        }
        print(body)
        url = "https://api.us.uneeq.io/api/v1/avatar/"+sessionId+"/speak"
        response = requests.post(url, data = json.dumps(body), headers = headers)
        status_code = response.status_code
        return response.content
    else:
        options = Qdata["options"]
        Question = Qdata["Question"]
        AC ="Question "+str(Current)+". "+Question + "\n" 
        AC1 =str(Current)+". "+Question 
        
        
        # dici=json.dumps(dicinew)

        html =""
        # "<ul>\n"
        for option in options:
            html += f"{option}"
        # html += "</ul>"
        headers = { 
          "Content-Type": 'application/json'
        }
        encodedSessionIdJwt = jwt.encode({'sessionId': f'{sessionId}'}, sessionIdJwt, algorithm='HS256')

        
        dicinew = {
          "Question":AC,
          "options":options,
          "Output":"",
          "Test":"",
          "text": AC+html,
          "link":"",
          "imageUrl":"",
          "description":""
        }
        instruction = {
              "customData": dicinew
        }
        instructions={"instructions":instruction}
        data1 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+AC + html+'</mstts:express-as></voice></speak>'
        body = {
          'answer': data1,
          # 'answer':AC +html,
          'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
          # 'answerAvatar':instructions,
          'sessionIdJwt': encodedSessionIdJwt
        }
        print(body)
        Data=Token_Data.get_item(Key={'token' : token})
        # print(AC +options1+ listToStr)
        Data['Item']['Question']=Qdata
        Token_Data.put_item(Item=Data['Item'])
        url = "https://api.us.uneeq.io/api/v1/avatar/"+sessionId+"/speak"
        response = requests.post(url, data = json.dumps(body), headers = headers)
        status_code = response.status_code
        print(status_code)
        
        data111=json.dumps(body)
        print(data111)
        return response.content
