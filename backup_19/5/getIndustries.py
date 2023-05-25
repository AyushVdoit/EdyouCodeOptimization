import json
import boto3
from uuid import uuid4
dynamodb = boto3.resource('dynamodb')
Industries=dynamodb.Table('Industries')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False 


def lambda_handler(event, context):
    if TokenChecker(event['token']):
        response = Industries.scan()
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = Industries.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        result.sort(key = lambda x:x['created_at'],reverse =False)
            
        return {
            'statusCode': 200,
            'body': result
        }
        
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }