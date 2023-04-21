import json
import boto3

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data=Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False
	

# to update user info
def lambda_handler(event, context):
	if token_checker(event['token']):
		email = event['email'].lower()
		user_info=user.get_item(Key={'email' : email})
		if 'Item'in user_info:
			del event['token']
			if event['gptPromptUser']=="":
				event['gptPromptUser']="Everything"
			event['password']=user_info['Item']['password']
			user.put_item(Item=event)
		return {
			'statusCode': 200,
			'body': "updated successfully"
		}

