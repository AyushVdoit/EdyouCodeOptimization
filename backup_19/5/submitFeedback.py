import json
import boto3
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
user = dynamodb.Table("Investor")
InvestorLoginHistory = dynamodb.Table("InvestorLoginHistory")
feedback = dynamodb.Table("feedback")
def lambda_handler(event, context):
    now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
    InvestorLoginHistoryResponse = InvestorLoginHistory.get_item(Key={'email' :event['email'],'time':event['time']})
    InvestorLoginHistoryResponse = InvestorLoginHistoryResponse['Item']
    datanew = InvestorLoginHistoryResponse['data']
    last_five = datanew[-5:]

    dici={
        "email":event['email'],
        "lastlogin":event['time'],
        "time":now,
        "data":last_five,
        "feedback":event['feedback'],
        "emoji":event['emoji'],
        "name":event['name'],
        "website":"Investor"
        
    }
    
    feedback.put_item(Item=dici)

    return {
        'statusCode': 200,
        'body': 'Feedback added'
    }
