import json
import boto3

dynamodb = boto3.resource('dynamodb')
Question = dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
    data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  

# to delete question header with given input id
def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["id"]
		# check if required fields are present
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            if event['status']=='Inactive':
                for id in event['id']:
                    question_info = Question.get_item(Key={'id' : id})
                    question_info['Item']['status']=event['status']
                    Question.put_item(Item=question_info['Item'])
                return {
                'statusCode': 200,
                'body': 'Test series deactivated successfully.'
                }
            elif event['status']=='Active':
                for id in event['id']:
                    question_info = Question.get_item(Key={'id' : id})
                    question_info['Item']['status']=event['status']
                    Question.put_item(Item=question_info['Item'])
                return {
                    'statusCode': 200,
                    'body': f'Test series activated successfully.'
                }
            elif  event['status']=='Delete':
                for id in event['id']:
                    question_info = Question.get_item(Key={'id' : id})
                    question_info['Item']['status']=event['status']
                    Question.put_item(Item=question_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Test series deleted successfully.'
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Error'
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
        
