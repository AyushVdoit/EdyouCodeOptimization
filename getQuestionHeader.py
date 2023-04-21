import json
import boto3

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
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
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			# scan Question Table
			questions = Question.scan()
			result = questions['Items']
			while 'LastEvaluatedKey' in questions:
				questions = Question.scan(ExclusiveStartKey=questions['LastEvaluatedKey'])
				result.extend(questions['Items'])
			tenant_list=[]
			admin_list=[]
			if 'email' not in event:
				event['email']=""
				event['role']=""
			for question in result:
				question_info={}
				question_info['id']=question["id"]
				question_info["topic"]=question["topic"]
				question_info["description"]=question["description"]
				question_info["max_marks"]=question["max_marks"]
				question_info["no_of_question"]=question['no_of_question']
				question_info["series_title"]=question['series_title']
				question_info['Tenantemail']=question['Tenantemail']
				question_info['name']=question['name']
				if event['email']==question['Tenantemail']:
					tenant_list.append(question_info)
				if event['role']=="Admin":
					admin_list.append(question_info)
			
			# if role is admin then return admin list else return tenant list
			if event['role']=="Admin":
				if len(admin_list)>0:
					return {
						'statusCode': 200,
						'body': admin_list
					}
				else:
					return {
						'statusCode': 205,
						'body': "No test series is added yet"
					}
			else:
				if len(tenant_list)>0:
					return {
						'statusCode': 200,
						'body': tenant_list
					}
				else:
					return {
						'statusCode': 205,
						'body': "No test series is added yet"
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
	