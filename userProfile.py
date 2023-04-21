import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
import string
import random
import requests
import smtplib

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  
	
def lambda_handler(event, context):
	# try:
	data =event
	# check if required fields are present
	required_fields = ["email","token"]
	for field in required_fields:
		if field not in data or not data[field]:
			return {
			'statusCode': 400,
			'body': f'Error: {field} is required and cannot be empty'
			}
	if token_checker(event['token']):
		email = event['email']
		email=email.lower()
		# get user info matching with email
		user_info =user.get_item(Key={'email':email})
		if 'Item' in user_info:
			if user_info['Item']['role']=='User':
				name=user_info['Item']['name']
				if 'SessionID' in event:
					payload_data={
						'sessionId':event['SessionID'],
						'token':event['token'],
						'Qdata':f"This is the profile page of {name}.",
						"Current":1
					}
					url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/uneeq/unsolicitedResponses"
					payload = json.dumps(payload_data, default=decimal_default)
					headers = {
					  'Content-Type': 'application/json'
					}
					response = requests.request("POST", url, headers=headers, data=payload)
				else:
					pass
				return {
					'statusCode': 200,
					'data':user_info['Item'],
					'body': 'User Profile'
				}
			else:
				
				return {
					'statusCode': 401,
					'body': 'Invalid Credentials'
				}
		else:
			return {
				'statusCode': 401,
				'body': 'Invalid Credentials'
			}
	else:
		return {
			'statusCode': 401,
			'body': 'Token is Invalid please re-login'
		}
	
	# except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
		# return {
		#     'statusCode': 400,
		#     'body': f'Error: {e}'
		# }

def decimal_default(obj):
	if isinstance(obj, Decimal):
		return str(obj)
	raise TypeError