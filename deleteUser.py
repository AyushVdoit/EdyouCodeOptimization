import json
import boto3

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data :
		return True
	else:
		return False  
	
def lambda_handler(event, context):
	try:
		data = event
		required_fields = ["token","email","status"]
		# check if required fields are present
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			email = event['email'].lower()
			# to delete user account
			if event['status']=='Delete':
				response = user.delete_item(
				Key={
					'email': email,
					},
				)
				if "role" in event:
					msg = event['role']
				else:
					msg ="User"
				return {
					'statusCode': 200,
					'body': f'{msg} deleted successfully'
				}
			# to deactivate user
			elif event['status']=="Deactivate":
				resp=user.get_item(Key={'email' : email})
				data = resp['Item']
				data['status']="Inactive"
				user.put_item(Item=data)
				return {
					'statusCode': 401,
					'body': 'Deactivated successfully'
				}
			# to activate user
			elif event['status']=="Activate":
				resp=user.get_item(Key={'email' : email})
				data = resp['Item']
				data['status']="Active"
				user.put_item(Item=data)
				return {
					'statusCode': 401,
					'body': 'Activated successfully'
				}

			else:
				return {
					'statusCode': 401,
					# ?body can be changed
					'body': 'done'
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
	
