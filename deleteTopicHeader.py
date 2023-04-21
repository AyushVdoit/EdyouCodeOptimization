import json
import boto3

dynamodb = boto3.resource('dynamodb')
Topic = dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')
		
def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  


def lambda_handler(event, context):
	try:
		data =event
		required_fields = ["token"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
			
		if token_checker(event['token']):
			if event['status']=='Inactive':
				for id in event['Topic_id']:
					topic_info = Topic.get_item(Key={'Topic_id' : id})
					topic_info['Item']['status']=event['status']
					Topic.put_item(Item=topic_info['Item'])
				return {
				'statusCode': 200,
				'body': 'Topic deactivated successfully'
				}
			elif event['status']=='Active':
				for id in event['Topic_id']:
					topic_info = Topic.get_item(Key={'Topic_id' : id})
					topic_info['Item']['status']=event['status']
					Topic.put_item(Item=topic_info['Item'])
				return {
					'statusCode': 200,
					'body': f'Topic activated successfully'
				}
			elif  event['status']=='Delete':
				for id in event['Topic_id']:
					topic_info = Topic.delete_item(Key={'Topic_id' : id})
				return {
					'statusCode': 200,
					'body': 'Topic deleted successfully'
				}
			else:
				return {
					'statusCode': 400,
					'body': 'Error'
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
