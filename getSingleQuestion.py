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
	
def lambda_handler(event, context):
	try:
		
		data =event
		required_fields = ["token","id"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
				# response ={
				#     'statusCode': 400,
				#     'body': f'Error: {field} is required and cannot be empty'
				#     }
				# callback(null, response)
		
		if token_checker(event['token']):
			questions =Question.get_item(Key={'id':event['id']})
			if 'Item' in questions:
				# size = len(questions['Item']['question'])
				stored_questions =questions['Item']['question']
				for question in stored_questions:
					if question['qid'] ==event['qid']:
						break
				question['correctAnswer']=question['correctAnswer'][3:]
				for j in range(len(question['description'])):
					if j != question['correctPostioin']:
						question['description'][j]=question['description'][j][2:]
						question['description'][j] = question['description'][j].replace("is incorrect because ","")
					else:
						question['description'][j]=question['description'][j][2:]
						question['description'][j] = question['description'][j].replace("is correct because ","")
				
				for j in range(len(question['options'])):
					question['options'][j] = question['options'][j][3:]    
				return {
					'statusCode': 200,
					'body': question
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
