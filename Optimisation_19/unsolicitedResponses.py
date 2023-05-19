import boto3
import json
import jwt
import os
import requests

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB table
token_data = dynamodb.Table('Token')

def lambda_handler(event, context):
    # Constants
    session_Id_JWT = "CF537D5E-A1AE-C1E1-1244-CA9B4856A127"
    
    # Extract data from the event
    session_Id = event['sessionId']
    token = event['token']
    Qdata = event['Qdata']
    Current = event['Current']
    
    # Check the type of Qdata
    if type(Qdata) == type(token):
        # Qdata is a string
        
        # Set headers for the API request
        headers = {
            "Content-Type": 'application/json'
        }
        
        # Encode sessionId into a JWT token
        encodedSessionIdJwt = jwt.encode({'sessionId': f'{session_Id}'}, session_Id_JWT, algorithm='HS256')
        
        # Prepare the instruction for the avatar
        instruction = {
            "customData": {
                'Question': "",
                "options": [],
                "Output": Qdata,
                "Test": "",
                "text": Qdata,
                "link": "",
                "imageUrl": ""
            }
        }
        
        # Prepare the data for the TTS (Text-to-Speech)
        data4 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">' + Qdata + '</mstts:express-as></voice></speak>'
        
        # Prepare the request body
        body = {
            'answer': data4,
            'answerAvatar': json.dumps(instruction, separators=(',', ':'), ensure_ascii=False),
            'sessionIdJwt': encodedSessionIdJwt
        }
        
        # Send the request to the avatar API
        url = "https://api.us.uneeq.io/api/v1/avatar/" + session_Id + "/speak"
        response = requests.post(url, data=json.dumps(body), headers=headers)
        status_code = response.status_code
        
        return response.content
    else:
        # Qdata is a dictionary
        
        # Extract options and question from Qdata
        options = Qdata["options"]
        Question = Qdata["Question"]
        
        # Prepare the formatted question and options
        AC = "Question " + str(Current) + ". " + Question + "\n"
        AC1 = str(Current) + ". " + Question
        
        html = ""
        for option in options:
            html += f"{option}"
        
        headers = { 
            "Content-Type": 'application/json'
        }
        
        encodedSessionIdJwt = jwt.encode({'sessionId': f'{session_Id}'}, session_Id_JWT, algorithm='HS256')
        
        # Prepare the instruction for the avatar
        dicinew = {
            "Question": AC,
            "options": options,
            "Output": "",
            "Test": "",
            "text": AC + html,
            "link": "",
            "imageUrl": "",
            "description": ""
        }
        
        # Prepare the instructions
        instruction = {
            "customData": dicinew
        }
        instructions = {"instructions": instruction}
        
        # Prepare the data for the TTS (Text-to-Speech)
        data1 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">' + AC + html + '</mstts:express-as></voice></speak>'
        
        # Prepare the request body
        body = {
            'answer': data1,
            'answerAvatar': json.dumps(instructions, separators=(',', ':'), ensure_ascii=False),
            'sessionIdJwt': encodedSessionIdJwt
        }
        
        # Update the token data in DynamoDB
        Data = token_data.get_item(Key={'token': token})
        Data['Item']['Question'] = Qdata
        token_data.put_item(Item=Data['Item'])
        
        # Send the request to the avatar API
        url = "https://api.us.uneeq.io/api/v1/avatar/" + session_Id + "/speak"
        response = requests.post(url, data=json.dumps(body), headers=headers)
        status_code = response.status_code
        
        data111 = json.dumps(body)
        
        return response.content
