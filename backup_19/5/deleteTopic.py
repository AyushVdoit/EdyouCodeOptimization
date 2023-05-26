import json
import boto3

dynamodb = boto3.resource('dynamodb')
Topic=dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
    data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["Topic_id","token","qid"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            # fetch topic info with matching topic id
            topic_info = Topic.get_item(Key={'Topic_id':event['Topic_id']})
            if 'Item' in topic_info:
                question=topic_info['Item']['question']
                updated_questions = [i for i in question if not (i['qid'] == event['qid'])]
                topic_info['Item']['question'] = updated_questions
                Topic.put_item(Item=topic_info['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Topic deleted Successfully'
                    }
            
                    
            else:
                
                return {
                'statusCode': 200,
                'body': 'No item Found'
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