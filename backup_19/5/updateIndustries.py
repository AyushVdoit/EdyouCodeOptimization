import json
import boto3
from uuid import uuid4
dynamodb = boto3.resource('dynamodb')
Industries=dynamodb.Table('Industries_Prod')
Token_Data = dynamodb.Table('Token_Prod')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    if TokenChecker(event['token']):
        del event['token']
        Industries.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Industry updated successfully"
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
    
    
