import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Topic=dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')

# to verify the token
def token_checker(token):
	Data=Token_Data.get_item(Key={'token' : token})
	if 'Item' in Data:
		return True
	else:
		return False  
	
def lambda_handler(event, context):
	try:
		data =event

		# check if required fields are present 
		required_fields = ["token","topicName","description"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
			
		# if token is valid
		if token_checker(event['token']):
			unique_id = uuid4().hex
			topic_info = {}
			if event['email'] in ['admin@edyou.com','admin@edyou.in']:
				if event['tenantEmail']=="":
					event['email']=""
				else:
					event['email']=event['tenantEmail']
			topic_info['Tenantemail']=event['email']
			if topic_info['Tenantemail']!="":
				user_info = user.get_item(Key={'email' : topic_info['Tenantemail'].lower()})
				if 'Item' in user_info:
					topic_info['name']=user_info['Item']['name']
			else:
				topic_info['name']=""
				
			topic_info['Topic_id']=unique_id
			topic_info['topicName']=event['topicName']
			topic_info['question']=[]
			topic_info['industry']=event['industry']
			topic_info['description']=event['description']
			topic_info['status']=event['status']
			Topic.put_item(Item=topic_info) 
			return {
					'statusCode': 200,
					'id': unique_id,
					"body":"New Topic is Added"
				}
		# if token is invalid
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
