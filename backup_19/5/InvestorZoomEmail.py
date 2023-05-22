import json
import boto3
import os
dynamodb = boto3.resource('dynamodb')
Token_Data = dynamodb.Table('Token')
Investor = dynamodb.Table("Investor")

def lambda_handler(event, context):
    email = event['email']
    sessionID = event['sessionID']
    Data=Investor.get_item(Key={'email' : event['email'].lower()})
    Data['Item']['sessionID']=event['sessionID']
    Data['Item']['token']=event['token']
    Investor.put_item(Item=Data['Item'])
    
    return {
        'statusCode': 200,
        'body': "Session id saved"
    }
    
