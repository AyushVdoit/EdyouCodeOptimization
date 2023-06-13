import json
import boto3
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('InvestorLoginHistory')
Token_Data = dynamodb.Table('Token')
Token_Data_Prod = dynamodb.Table('Token_Prod')

def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        Data=Token_Data_Prod.get_item(Key={'token' : token})
        if 'Item' in Data:
            return True
        else:
            return False 

def lambda_handler(event, context):
    if TokenChecker(event['token']):
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        now1 = "2023-02-02,00:00:00"
        resp=Investor.query(KeyConditionExpression=Key('email').eq(event['email'])& Key('time').between(now1,now),ScanIndexForward=False)
        # if 'Item' in Data:
        l=[]
        for i in resp['Items']:
            conversation="not started"
            if len(i['data'])!=0:
                conversation ="started"
                
            dici={
                'email':i['email'],
                'time':i['time'],
                'conversation':conversation,
                "logout":i['logout'],
                "Session":i['Session'],
                "Ip_Address":i['Ip_Address']
            }
            l.append(dici)
        return{
            'statusCode':200,
            'body':l
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
    