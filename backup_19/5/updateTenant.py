import json
import boto3
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
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
        email = event['email'].lower()
        resp=user.get_item(Key={'email' : email})
        if 'Item'in resp:
            del event['token']
            Data=Industries.get_item(Key={'id' : event['industry']})
            if 'Item' in Data:
                event['industryName']=Data['Item']['name']
            event['password']=resp['Item']['password']
            
            user.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Tenant updated successfully"
        }

