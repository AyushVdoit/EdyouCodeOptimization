import json
import boto3
from uuid import uuid4
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question_Prod')
user=dynamodb.Table('user_Prod')
Token_Data = dynamodb.Table('Token_Prod')
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
        required_fields = ["token","description","max_marks","series_title","no_of_question"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            unique_id=uuid4().hex
            questionDicitionary={}
            if event['email'] in ['admin@edyou.com','admin@edyou.in']:
                if event['tenantEmail']=="" or event['tenantEmail']=="none":
                    event['email']=""
                else:
                    event['email']=event['tenantEmail']
            questionDicitionary['Tenantemail']=event['email']
            
            if questionDicitionary['Tenantemail']!="":
                Data=user.get_item(Key={'email' : questionDicitionary['Tenantemail'].lower()})
                if 'Item' in Data:
                    questionDicitionary['name']=Data['Item']['name']
            else:
                questionDicitionary['name']=""
            questionDicitionary['id']=unique_id
            questionDicitionary['topic']=event['topic']
            questionDicitionary['question']=[]
            questionDicitionary['description']=event['description']
            questionDicitionary['max_marks']=event['max_marks']
            questionDicitionary['no_of_question']=event['no_of_question']
            questionDicitionary['series_title']=event['series_title']
            # questionDicitionary['rules']=event['rules']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            questionDicitionary['created_at']=now
            questionDicitionary['status']=event['status']
            Question.put_item(Item=questionDicitionary) 
            return {
                    'statusCode': 200,
                    'id': unique_id,
                    "body":"Test series added successfully"
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