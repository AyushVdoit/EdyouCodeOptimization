import json
import boto3
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
        required_fields = ["email","token","f_name","l_name","contact"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            resp=user.get_item(Key={'email' : event['email']})
            if "Item" in resp:
                resp['Item']['email']= event['email']
                resp['Item']['name']= event['f_name']+" "+event['l_name']
                resp['Item']['l_name'] = event['l_name']
                resp['Item']['f_name']=event['f_name']
                resp['Item']['contact']=event['contact']
            user.put_item(Item=resp['Item'])
            return {
                'statusCode': 200,
                'body': 'Profile Updated',
                'Data':resp['Item']
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