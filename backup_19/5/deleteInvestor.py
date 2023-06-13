import json
import boto3
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
    data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["token","email"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            print(event)
            email = event['email'].lower()
            response = Investor.delete_item(Key={'email': email},)    
            return {
                'statusCode': 200,
                'body': 'Investor deleted successfully'
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
    
