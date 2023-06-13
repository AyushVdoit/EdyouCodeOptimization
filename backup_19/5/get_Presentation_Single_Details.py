import json
import boto3
dynamodb = boto3.resource('dynamodb')
Presentation=dynamodb.Table('Presentation')
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
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
        # TODO implement
            presentation_details=Presentation.get_item(Key={'id' : event['id']})
            if 'Item' in presentation_details:
                return{
                    'statusCode':200,
                    'body':presentation_details['Item']
                }
            else:
                return{
                    'statusCode':200,
                    'body':"error no such file"
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
    