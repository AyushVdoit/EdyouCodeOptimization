import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
from time import gmtime, strftime

user=dynamodb.Table('user')
Topic=dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    # TODO implement
    try:
        data =event
        required_fields = ["token","topicName","description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            
            unique_id=uuid4().hex
            topicDicitionary={}
            if event['email'] in ['admin@edyou.com','admin@edyou.in']:
                if event['tenantEmail']=="":
                    event['email']=""
                else:
                    event['email']=event['tenantEmail']
            topicDicitionary['Tenantemail']=event['email']
            if topicDicitionary['Tenantemail']!="":
                Data=user.get_item(Key={'email' : topicDicitionary['Tenantemail'].lower()})
                if 'Item' in Data:
                    topicDicitionary['name']=Data['Item']['name']
            else:
                topicDicitionary['name']=""
                
            topicDicitionary['Topic_id']=unique_id
            topicDicitionary['topicName']=event['topicName']
            topicDicitionary['question']=[]
            topicDicitionary['industry']=event['industry']
            topicDicitionary['description']=event['description']
            topicDicitionary['status']=event['status']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            topicDicitionary['created_at']=now
            Topic.put_item(Item=topicDicitionary) 
            return {
                    'statusCode': 200,
                    'id': unique_id,
                    "body":"Topic added successfully"
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }
        
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
