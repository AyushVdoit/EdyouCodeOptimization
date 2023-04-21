import json
import boto3
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
industries = dynamodb.Table('Industries')
Token_Data = dynamodb.Table('Token')

# to verify the token
def token_checker(token):
	data =Token_Data.get_item(Key={'token' : token})
	if 'Item' in data :
		return True
	else:
		return False  

# to insert an industry 
def lambda_handler(event, context):

	# if token is valid
	if token_checker(event['token']):
		uuid_inserted = uuid4().hex
		event['id'] = uuid_inserted
		industries.put_item(Item=event)
		return {
			'statusCode': 200,
			'body': "added successfully"
		}
	
	# if token is not valid
	else:
		return {
			'statusCode': 401,
			'body': 'Token is Invalid please re-login'
		}
	
	
