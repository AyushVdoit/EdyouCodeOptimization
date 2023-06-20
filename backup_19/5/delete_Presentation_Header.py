import json
import boto3
dynamodb = boto3.resource('dynamodb')
Presentation = dynamodb.Table('Presentation')
Token_Data = dynamodb.Table('Token')
def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            if event['status']=='Inactive':
                for i in event['id']:
                    resp = Presentation.get_item(
                    Key={
                        'id' : i
                    }
                    )
                    resp['Item']['status']=event['status']
                    Presentation.put_item(Item=resp['Item'])
                return {
                'statusCode': 200,
                'body': 'Learning deactivated successfully.'
                }
            elif event['status']=='Active':
                for i in event['id']:
                    resp = Presentation.get_item(
                    Key={
                        'id' : i
                    }
                    )
                    resp['Item']['status']=event['status']
                    Presentation.put_item(Item=resp['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Learning activated successfully.'
                }
            elif  event['status']=='Delete':
                for i in event['id']:
                    resp = Presentation.get_item(
                    Key={
                        'id' : i
                    }
                    )
                    resp['Item']['status']=event['status']
                    Presentation.put_item(Item=resp['Item'])
                

                    # resp = Presentation.delete_item(Key={'id' : i})
                return {
                    'statusCode': 200,
                    'body': 'Learning deleted successfully.'
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
        
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  