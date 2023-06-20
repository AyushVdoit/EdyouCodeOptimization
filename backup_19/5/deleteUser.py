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
        required_fields = ["token","email","status"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            print(event)
            email = event['email'].lower()
            
            if event['status']=='Delete':
                response = user.delete_item(
                Key={
                    'email': email,
                    },
                )
                if "role" in event:
                    msg = event['role']
                else:
                    msg ="User"
                return {
                    'statusCode': 200,
                    'body': f'{msg} deleted successfully'
                }
            elif event['status']=="Deactivate":
                resp=user.get_item(Key={'email' : email})
                data = resp['Item']
                data['status']="Inactive"
                user.put_item(Item=data)
                return {
                    'statusCode': 401,
                    'body': 'Deactivate successfully'
                }
            elif event['status']=="Activate":
                resp=user.get_item(Key={'email' : email})
                data = resp['Item']
                data['status']="Active"
                user.put_item(Item=data)
                return {
                    'statusCode': 401,
                    'body': 'Activate successfully'
                }

            else:
                return {
                    'statusCode': 401,
                    'body': 'done'
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
    
