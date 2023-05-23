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
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
        # TODO implement
            response = user.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = user.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            l=[]
            for i in result:
                if i['role'] =="User":
                    l.append(i)
            
            l.sort(key = lambda x:x['created_at'])
            if len(l)>0:
                return {
                    'statusCode': 200,
                    'body': l
                }
            else:
                return {
                        'statusCode': 205,
                        'body': "No user are added yet"
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
    
