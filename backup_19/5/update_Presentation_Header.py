import json
import boto3
from uuid import uuid4
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Presentation=dynamodb.Table('Presentation')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    # TODO implement
    try:
        data =event
        required_fields = ["token","title"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            result=Presentation.get_item(Key={'id': event['id']})
            if 'Item' in result:
                PresentationDicitionary=result['Item']
                PresentationDicitionary['title']=event['title']
                PresentationDicitionary['description']=event['description']
                Presentation.put_item(Item=PresentationDicitionary) 
                return {
                        'statusCode': 200,
                        "body":"Learning updated successfully"
                    }
            else:
                return {
                        'statusCode': 200,
                        "body":"E"
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


