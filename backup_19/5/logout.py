import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import datetime
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('Investor')
InvestorLoginHistory = dynamodb.Table('InvestorLoginHistory')
Token_Data = dynamodb.Table('Token')
Token_Data_Prod = dynamodb.Table('Token_Prod')

def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
            return False 
def lambda_handler(event, context):
    if TokenChecker(event['token']):
        # TODO implement
        Data=InvestorLoginHistory.get_item(Key={'email' : event['email'].lower(),'time':event['time']})
        if 'Item' in Data:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            time2 = datetime.strptime(now, '%Y-%m-%d,%H:%M:%S')

            time1 = datetime.strptime(event['time'], '%Y-%m-%d,%H:%M:%S')
            # calculate the time difference
            time_diff =time2 - time1
            Data['Item']['logout'] =now
            Data['Item']['Session'] =str(time_diff)
            InvestorLoginHistory.put_item(Item=Data['Item'])
            return {
                'statusCode': 200,
                'body': "logout"
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Error'
            }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }