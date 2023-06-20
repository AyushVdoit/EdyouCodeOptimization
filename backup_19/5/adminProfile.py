import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
import string
import random
import smtplib
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["email","token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            email = event['email']
            email=email.lower()
            data2 =user.get_item(Key={'email':email})
            if 'Item' in data2:
                if data2['Item']['role']!='User':
                    return {
                        'statusCode': 200,
                        'data':data2['Item'],
                        'body': 'Admin Profile'
                    }
                else:
                    
                    return {
                        'statusCode': 401,
                        'body': 'Bad Credentials'
                    }
            else:
                return {
                    'statusCode': 401,
                    'body': 'Bad Credentials'
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