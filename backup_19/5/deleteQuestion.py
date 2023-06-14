import json
import boto3

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data=Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  
		
# to delete a question with matching qid
def lambda_handler(event, context):
	try:
		data =event
		required_fields = ["id","token","qid"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			questions =Question.get_item(Key={'id':event['id']})
			if 'Item' in questions:
				stored_questions=questions['Item']['question']
				updated_questions = [i for i in stored_questions if not (i['qid'] == event['qid'])]
				questions['Item']['question'] = updated_questions
				Question.put_item(Item=questions['Item']) 
		
				return {
				'statusCode': 200,
				
				'body': 'Question deleted Successfully'
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