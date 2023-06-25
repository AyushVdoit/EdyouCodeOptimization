import json
import boto3
from uuid import uuid4
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Presentation=dynamodb.Table('Presentation')
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
        required_fields = ["token","title"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            unique_id=uuid4().hex
            PresentationDicitionary={}
            if event['email'] in ['admin@edyou.com','admin@edyou.in']:
                if event['tenantEmail']=="":
                    event['email']=""
                else:
                    event['email']=event['tenantEmail']
            PresentationDicitionary['Tenantemail']=event['email']
            if PresentationDicitionary['Tenantemail']!="":
                Data=user.get_item(Key={'email' : PresentationDicitionary['Tenantemail'].lower()})
                if 'Item' in Data:
                    PresentationDicitionary['name']=Data['Item']['name']
            else:
                PresentationDicitionary['name']=""
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            PresentationDicitionary['created_at']=now
            PresentationDicitionary['id']=unique_id
            PresentationDicitionary['title']=event['title']
            PresentationDicitionary['description']=event['description']
            PresentationDicitionary['URL']=""
            PresentationDicitionary['Data']=[]
            PresentationDicitionary['status']=event['status']
            Presentation.put_item(Item=PresentationDicitionary) 
            return {
                    'statusCode': 200,
                    'id': unique_id,
                    "body":"Learning added successfully"
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


