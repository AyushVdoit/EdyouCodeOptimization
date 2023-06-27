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
        # data =event
        # required_fields = ["id","token","qid"]
        # for field in required_fields:
        #     if field not in data or not data[field]:
        #         return {
        #         'statusCode': 400,
        #         'body': f'Error: {field} is required and cannot be empty'
        #         }
        if TokenChecker(event['token']):
            email = event['email']
            email=email.lower()
            data2 =user.get_item(Key={'email':email})
            
            if 'Item' in data2:
                data2['Item']["name"] = event["f_name"] + " " + event["l_name"]
                data2['Item']['f_name']=event['f_name']
                data2['Item']['l_name']=event['l_name']
                data2['Item']['phone']=event['phone']
                data2['Item']['DOB']=event['DOB']
                data2['Item']['gender']=event['gender']
                data2['Item']['school']=event['school']
                data2['Item']['zip']=event['zip']
                data2['Item']['country']=event['country']
                data2['Item']['state']=event['state']
                data2['Item']['gpt3'] = event['gpt3']
                user.put_item(Item=data2['Item'])
                return {
                    'statusCode': 200,
                    'data':data2['Item'],
                    'body': 'Profile Updated'
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