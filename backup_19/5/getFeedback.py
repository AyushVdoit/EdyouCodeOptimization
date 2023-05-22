import json
import boto3
dynamodb = boto3.resource('dynamodb')
feedback=dynamodb.Table('feedback')
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
            response = feedback.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = feedback.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            # l=[]
            # for i in result:
            #     dici={
            #         "email":i['email'],
            #         "time":i["time"],
            #         "emoji":i["emoji"],
            #         "name":i['name']}
            #     l.append(dici)
            result.sort(key = lambda x:x['time'],reverse =True)
            return {
                    'statusCode': 200,
                    'body': result
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
    
