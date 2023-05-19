import json
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Topic=dynamodb.Table('Topic')

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
        required_fields = ["token","Topic_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        
        if TokenChecker(event['token']):
            data2 =Topic.get_item(Key={'Topic_id':event['Topic_id']})
            if 'Item' in data2:
                size = len(data2['Item']['question'])
                l=[]
                for i in data2['Item']['question']:
                    string=i['correctAnswer']
                    i['correctAnswer']=string.split("7481903939")[0]
                    l.append(i)
                if size>0:
                    return {
                        'statusCode': 200,
                        'body': l
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No questions are added yet"
                    }
            else:
                return {
                    'statusCode': 400,
                    'body': 'No data found'
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
