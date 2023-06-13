import json
import boto3
dynamodb = boto3.resource('dynamodb')
Industries=dynamodb.Table('Industries')
Token_Data=dynamodb.Table('Token')
def token_checker(token):
    data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["token","id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            response = Industries.delete_item(Key={'id': event['id']})    
            return {
                'statusCode': 200,
                'body': 'Industry deleted successfully'
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