import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from decimal import Decimal
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')
Question_Data = dynamodb.Table('Question')
Record = dynamodb.Table('Record')
def lambda_handler(event, context):
    # TODO implement
    resp = Record.get_item(Key={'userId' :event['email'],'QuestionId':event['id']})
    Token = Token_Data.get_item(Key={'token':event['token']})
    Token['Item']['QuestionId']=event['id']
    Token_Data.put_item(Item=Token['Item'])
    userData=user.get_item(Key={'email' : event['email']})
    userData=userData['Item']
    
    if 'restart' in event:
        Qdata = Question_Data.get_item(Key={'id':event['id']})
        
        dici={
            "userId":event['email'],
            "QuestionId":event['id'],
            "Token":event['token'],
            "Question":Qdata['Item']['question'],
            "CurrentPostion":0,
            'TestSeriesStatus':"Resume",
            "Total Question":len(Qdata['Item']['question']),
            "CorrectAnswerbyYou":0,
            "CurrentAnswerPostion":0
        }
        
        Record.put_item(Item = dici)
        
        # CurrentPostion=dici["CurrentPostion"]
        dici1={
            'sessionId':event['SessionID'],
            'token':event['token'],
            'Qdata':dici['Question'][dici["CurrentPostion"]],
            "Current":1

        }
        url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
        userData['StartTestSeries']=True
        user.put_item(Item = userData)
        payload = json.dumps(dici1, default=decimal_default)
        headers = {
          'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return {
            'statusCode': 200}

        
    if 'Item' in resp:
        userData['StartTestSeries']=True
        user.put_item(Item = userData)
        dici = resp['Item']
        CurrentPostion=int(dici["CurrentPostion"])
        CurrentAnswerPostion = int(dici["CurrentAnswerPostion"])
        if CurrentPostion<=dici['Total Question']-1:
            if CurrentPostion ==0:
                Qdata = Question_Data.get_item(Key={'id':dici['QuestionId']})
                dici["Total Question"]=len(Qdata['Item']['question'])
                dici['Question']=Qdata['Item']['question']
                Record.put_item(Item = dici)
            
            if CurrentAnswerPostion == CurrentPostion:
                # Qdata = Question_Data.get_item(Key={'id':dici['QuestionId']})
                # dici["Total Question"]=len(Qdata['Item']['question'])
                # dici['Question']=Qdata['Item']['question']
                # Record.put_item(Item = dici)
            
                dici1={
                    'sessionId':event['SessionID'],
                    'token':event['token'],
                    'Qdata':dici['Question'][CurrentPostion],
                    "Current":CurrentPostion+1
                }
                url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
                
                payload = json.dumps(dici1, default=decimal_default)
                headers = {
                  'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                
                if CurrentPostion == 0 and CurrentAnswerPostion == 0:
                    dici['CorrectAnswerbyYou']=0
                    Record.put_item(Item = dici)
                    
                # dici['CurrentPostion'] = int(dici["CurrentPostion"])+1
                # dici['CurrentAnswerPostion'] = int(dici["CurrentAnswerPostion"])+1
                # Record.put_item(Item = dici)
            
            
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
        else:
            Qdata = Question_Data.get_item(Key={'id':dici['QuestionId']})
            dici["Total Question"]=len(Qdata['Item']['question'])
            dici['Question']=Qdata['Item']['question']
            dici['CurrentPostion'] = 0
            dici['CurrentAnswerPostion'] = 0
            dici['TestSeriesStatus'] = 0
            Record.put_item(Item = dici)
            dici1={
                'sessionId':event['SessionID'],
                'token':event['token'],
                'Qdata':"You have already completed the test. To restart please say or write 'stop' the exit and start the test again.",
                "Current":0

            }
            url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
            
            payload = json.dumps(dici1, default=decimal_default)
            headers = {
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            
            
            
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda 1')
            }
    else:
        Qdata = Question_Data.get_item(Key={'id':event['id']})
        Token=Token_Data.get_item(Key={'token' : event['token']})
        
        dici={
            "userId":event['email'],
            "QuestionId":event['id'],
            "Token":event['token'],
            "Question":Qdata['Item']['question'],
            "CurrentPostion":0,
            "Total Question":len(Qdata['Item']['question']),
            "CorrectAnswerbyYou":0,
            "TestSeriesStatus":"Resume",
            "CurrentAnswerPostion":0
        }
        userData['StartTestSeries']=True
        user.put_item(Item = userData)
        Record.put_item(Item = dici)
        
        # CurrentPostion=dici["CurrentPostion"]
        dici1={
            'sessionId':event['SessionID'],
            'token':event['token'],
            'Qdata':dici['Question'][dici["CurrentPostion"]],
            "Current":1

        }
        url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
        
        payload = json.dumps(dici1, default=decimal_default)
        headers = {
          'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda 2')
        }

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError