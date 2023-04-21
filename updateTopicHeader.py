import json
import boto3
dynamodb = boto3.resource('dynamodb')
Topic = dynamodb.Table('Topic')
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
		required_fields = ["Topic_id","token","topicName","industry","description"]
		# check if required fields are present
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			# update topic header with input information
			Topic.update_item(
				Key={'Topic_id': event['Topic_id'],},
				UpdateExpression="set topicName=:topicName, description=:description, industry=:industry,status=:status",
				ExpressionAttributeValues={
						':topicName':event['topicName'],
						':industry':event['industry'],
						':description':event['description'],
						':status':event['status']
					},
				ReturnValues="UPDATED_NEW"
				)
			
			return {
				'statusCode': 200,
				'body': 'Information Updated Successfully'
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
