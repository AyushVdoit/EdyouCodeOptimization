import json
import boto3
from boto3.dynamodb.conditions import Key
from werkzeug.security import  check_password_hash, generate_password_hash
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
        required_fields = ["email","token","password","confpassword","oldpassword"]
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
                if check_password_hash(data2['Item']['password'],event['oldpassword']):
                    if event['password']==event['confpassword']:
                        data2['Item']['password']=generate_password_hash(event['confpassword'], method='sha256')
                        user.put_item(Item=data2['Item'])
                        return {'statusCode': 200,'body': 'Password Updated'}
                    else:
                        return {'statusCode': 400,'body': "Password didn't match"}
                else:
                    return {'statusCode': 400,'body': "Password didn't match with old passswor"}
            else:
                return {'statusCode': 400,'body': 'No user found'}
        
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