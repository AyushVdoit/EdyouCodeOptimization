import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data=Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  
	
# to get all the questions with given input id 
def lambda_handler(event, context):
	try:
		
		data = event

		required_fields = ["token","id"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		
		if token_checker(event['token']):
			question_info =Question.get_item(Key={'id':event['id']})
			if 'Item' in question_info:
				size = len(question_info['Item']['question'])
				if size>0:
					return {
						'statusCode': 200,
						'body': question_info['Item']['question']
					}
				else:
					return {
						'statusCode': 205,
						'body': "No questions are added yet"
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
