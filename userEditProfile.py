import json
import boto3

dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  

# to update user info
def lambda_handler(event, context):
	try:
		if token_checker(event['token']):
			email = event['email']
			email=email.lower()
			user_info = user.get_item(Key={'email':email})
			if 'Item' in user_info:
				user_info['Item']["name"] = event["f_name"] + " " + event["l_name"]
				user_info['Item']['f_name']=event['f_name']
				user_info['Item']['l_name']=event['l_name']
				user_info['Item']['phone']=event['phone']
				user_info['Item']['DOB']=event['DOB']
				user_info['Item']['gender']=event['gender']
				user_info['Item']['school']=event['school']
				user_info['Item']['zip']=event['zip']
				user_info['Item']['country']=event['country']
				user_info['Item']['state']=event['state']
				user_info['Item']['gpt3'] = event['gpt3']
				user.put_item(Item=user_info['Item'])
				return {
					'statusCode': 200,
					'data':user_info['Item'],
					'body': 'Profile Updated Successfully'
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