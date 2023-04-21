import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
User=dynamodb.Table('user')
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
		required_fields = ["token","description","max_marks","series_title","no_of_question"]
		# check if required fields are present
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
			
		if token_checker(event['token']):
			# create unique uuid
			unique_id=uuid4().hex
			questionDicitionary={}
			if event['email'] in ['admin@edyou.com','admin@edyou.in']:
				if event['tenantEmail']=="" or event['tenantEmail']=="none":
					event['email']=""
				else:
					event['email']=event['tenantEmail']
			questionDicitionary['Tenantemail']=event['email']
			
			if questionDicitionary['Tenantemail']!="":
				user_info = User.get_item(Key={'email' : questionDicitionary['Tenantemail'].lower()})
				if 'Item' in user_info:
					questionDicitionary['name']=user_info['Item']['name']
			else:
				questionDicitionary['name']=""
			questionDicitionary['id']=unique_id
			questionDicitionary['topic']=event['topic']
			questionDicitionary['question']=[]
			questionDicitionary['description']=event['description']
			questionDicitionary['max_marks']=event['max_marks']
			questionDicitionary['no_of_question']=event['no_of_question']
			questionDicitionary['series_title']=event['series_title']
			Question.put_item(Item=questionDicitionary) 
			return {
					'statusCode': 200,
					'id': unique_id,
					"body":"New Test Series Created"
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