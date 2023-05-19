import json
import boto3
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')
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
    try:
        data =event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
        # TODO implement
            Data=Investor.get_item(Key={'email' : event['email'].lower()})
            if 'Item' in Data:
                return{
                    'statusCode':200,
                    'body':Data['Item']
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
    
