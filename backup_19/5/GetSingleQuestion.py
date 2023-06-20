import json
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')

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
        required_fields = ["token","id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
                # response ={
                #     'statusCode': 400,
                #     'body': f'Error: {field} is required and cannot be empty'
                #     }
                # callback(null, response)
        
        if TokenChecker(event['token']):
            data2 =Question.get_item(Key={'id':event['id']})
            if 'Item' in data2:
                # size = len(data2['Item']['question'])
                question =data2['Item']['question']
                for i in question:
                    if i['qid'] ==event['qid']:
                        break
                    else:
                        pass
                i['correctAnswer']=i['correctAnswer'][3:]
                for j in range(len(i['description'])):
                    if j != i['correctPostioin']:
                        i['description'][j]=i['description'][j][2:]
                        i['description'][j] = i['description'][j].replace("is incorrect because ","")
                    else:
                        i['description'][j]=i['description'][j][2:]
                        i['description'][j] = i['description'][j].replace("is correct because ","")
                
                for j in range(len(i['options'])):
                    i['options'][j] = i['options'][j][3:]    
                return {
                    'statusCode': 200,
                    'body': i
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
