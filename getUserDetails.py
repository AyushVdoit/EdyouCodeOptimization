import json
import boto3

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
    data = Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  
    
def lambda_handler(event, context):
    try:
        data =event
        # check if required fields are present 
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            user_info=user.get_item(Key={'email' : event['email'].lower()})
            if 'Item' in user_info:
                return{
                    'statusCode':200,
                    'body':user_info['Item']
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
    
