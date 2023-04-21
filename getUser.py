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
def lambda_handler(event, context):

	try:
		data =event
		required_fields = ["token"]
		# check if required fields are present
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			# to fetch all the users
			user_data = user.scan()
			result = user_data['Items']
			while 'LastEvaluatedKey' in user_data:
				user_data = user.scan(ExclusiveStartKey=user_data['LastEvaluatedKey'])
				result.extend(user_data['Items'])
			# return list of users whose role is "User"
			users=[]
			for user in result:
				if user['role'] =="User":
					users.append(user)
			user.sort(key = lambda x:x['created_at'])
			if len(users)>0:
				return {
					'statusCode': 200,
					'body': users
				}
			else:
				return {
						'statusCode': 205,
						'body': "No user is added yet"
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
	
