import json
import boto3
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime


dynamodb = boto3.resource('dynamodb')
investor=dynamodb.Table('InvestorLoginHistory')
token_data = dynamodb.Table('Token')
token_data_prod = dynamodb.Table('Token_Prod')


def token_checker(token):
    Data=token_data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        Data=token_data_prod.get_item(Key={'token' : token})
        if 'Item' in Data:
            return True
        else:
            return False 


def lambda_handler(event, context):
    if token_checker(event['token']):
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        now1 = "2023-02-02,00:00:00"
        response=investor.query(KeyConditionExpression=Key('email').eq(event['email'])& Key('time').between(now1,now),ScanIndexForward=False)
        
        list=[]
        # check if the conversation is started or not
        for i in response['Items']:
            conversation="not started"
            if len(i['data'])!=0:
                conversation ="started"
            # create a dictionary which contains the data of the conversation 
            dict={
                'email':i['email'],
                'time':i['time'],
                'conversation':conversation,
                "logout":i['logout'],
                "Session":i['Session'],
                "Ip_Address":i['Ip_Address']
            }
            # add the dictionary into the list 
            list.append(dict)
        return{
            'statusCode':200,
            'body':list
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
    
