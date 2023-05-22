import json
import boto3
from uuid import uuid4
dynamodb = boto3.resource('dynamodb')
Websites=dynamodb.Table('Websites')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    if TokenChecker(event['token']):
        response = Websites.scan()
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = Websites.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        l=[]
        for i in result:
            if i['type']=="Dev":
                l.append(i)    
        l.sort(key = lambda x:x['created_At'])
        # ,reverse = True) 
                
        return {
            'statusCode': 200,
            'body': l
        }
        
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }