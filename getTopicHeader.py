import json
import boto3

dynamodb = boto3.resource('dynamodb')
Topic=dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')

# to verify the token
def token_checker(token):
	data=Token_Data.get_item(Key={'token' : token})
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
			response = Topic.scan()
			result = response['Items']
			while 'LastEvaluatedKey' in response:
				response = Topic.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
				result.extend(response['Items'])
			tenantlist=[]
			adminlist=[]
			if 'email' not in event:
				event['email']=""
				event['role']=""
			for topic in result:
				topic_info={}
				topic_info['Topic_id']=topic["Topic_id"]
				topic_info["topicName"]=topic["topicName"]
				topic_info['description']=topic['description']
				topic_info['industry']=topic["industry"]
				topic_info['status']=topic["status"]
				topic_info['Tenantemail']=topic['Tenantemail']
				topic_info['name']=topic['name']
				if event['email']==topic['Tenantemail']:
					tenantlist.append(topic_info)
				if event['role']=="Admin":
					adminlist.append(topic_info)
			if event['role']=="Admin":
				if len(adminlist)>0:
					return {
						'statusCode': 200,
						'body': adminlist
					}
				else:
					return {
						'statusCode': 205,
						'body': "No Topic is added yet"
					}
			else:
				if len(tenantlist)>0:
					return {
						'statusCode': 200,
						'body': tenantlist
					}
				else:
					return {
						'statusCode': 205,
						'body': "No Topic is added yet"
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
	
