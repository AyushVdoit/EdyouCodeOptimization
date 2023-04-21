import json
import boto3

dynamodb = boto3.resource('dynamodb')
investor=dynamodb.Table('InvestorLoginHistory')
Token_Data = dynamodb.Table('Token')
Token_Data_prod = dynamodb.Table('Token_Prod')

# to verify the token 
def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		data=Token_Data_prod.get_item(Key={'token' : token})
		if 'Item' in data:
			return True
		else:
			return False 

def lambda_handler(event, context):
	try:
		data = event
		required_fields = ["token"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		# if token is valid 
		if token_checker(event['token']):
			investor_data =investor.get_item(Key={'email' : event['email'].lower(),'time':event['time']})
			if 'Item' in investor_data :
				return{
					'statusCode':200,
					'body':investor_data ['Item']['data']
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
	
