import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
User = dynamodb.Table('Investor')
Question = dynamodb.Table('Question')
Record = dynamodb.Table('Record')
Token = dynamodb.Table('Token')

def lambda_handler(event, context):
	# TODO implement
	record_data  = Record.get_item(Key={'userId' :event['email'],'QuestionId':event['id']})
	user_data = User.get_item(Key={'email' : event['email']})
	user_data = user_data['Item']
	token_data = Token.get_item(Key={'token':event['token']})
	token_data['Item']['QuestionId']=event['id']
	Token.put_item(Item=token_data['Item'])
	
	# if user has asked to restart the test series 
	if 'restart' in event:
		# fetch question data from id 
		question_data = Question.get_item(Key={'id':event['id']})
		
		# update record data 
		updated_record_data = {
			"userId":event['email'],
			"QuestionId":event['id'],
			"Token":event['token'],
			"Question":question_data['Item']['question'],
			"CurrentPostion":0,
			'TestSeriesStatus':"Resume",
			"Total Question":len(question_data['Item']['question']),
			"CorrectAnswerbyYou":0,
			"CurrentAnswerPostion":0
		}
		Record.put_item(Item = updated_record_data)
		# CurrentPostion=updated_record_data["CurrentPostion"]


		payload_data={
			'sessionId':event['SessionID'],
			'token':event['token'],
			'email':event['email'],
			'question_data':updated_record_data['Question'][updated_record_data["CurrentPostion"]],
			"Current":1,
			'lastlogin':user_data['lastlogin'],
			'restart':'{restart}'
		}
		url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
		
		# update startTestSeries in user data to true
		user_data['StartTestSeries']=True
		User.put_item(Item = user_data)
		payload = json.dumps(payload_data, default=decimal_default)
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		
		return {
			'statusCode': 200}

	# to resume test series 
	# if there is a record with given email and question id
	if 'Item' in record_data:
		# update startTestSeries in user data to true
		user_data['StartTestSeries']=True
		User.put_item(Item = user_data)

		record_info = record_data['Item']
		CurrentPostion=int(record_info["CurrentPostion"])
		CurrentAnswerPostion = int(record_info["CurrentAnswerPostion"])

		# if current question is not the last question 
		if CurrentPostion<=record_info['Total Question']-1:

			# if current question is 1st question, update record info
			if CurrentPostion ==0:
				question_data = Question.get_item(Key={'id':record_info['QuestionId']})
				record_info["Total Question"]=len(question_data['Item']['question'])
				record_info['Question']=question_data['Item']['question']
				Record.put_item(Item = record_info)
			
			
			if CurrentAnswerPostion == CurrentPostion:
				payload_data={
					'sessionId':event['SessionID'],
					'token':event['token'],
					'email':event['email'],
					'question_data':record_info['Question'][CurrentPostion],
					"Current":CurrentPostion+1,
					'lastlogin':user_data['lastlogin'],
					"restart":"{resume}"
				}
				url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
				payload = json.dumps(payload_data, default=decimal_default)
				headers = {
				  'Content-Type': 'application/json'
				}
				response = requests.request("POST", url, headers=headers, data=payload)
				
				if CurrentPostion == 0 and CurrentAnswerPostion == 0:
					record_info['CorrectAnswerbyYou']=0
					Record.put_item(Item = record_info)
					
				# record_info['CurrentPostion'] = int(record_info["CurrentPostion"])+1
				# record_info['CurrentAnswerPostion'] = int(record_info["CurrentAnswerPostion"])+1
				# Record.put_item(Item = record_info)
			
		
			return {
				'statusCode': 200,
				'body': json.dumps('Hello from Lambda 1')
			}
		
		# if current question is the last question 
		else:
			question_data = Question.get_item(Key={'id':record_info['QuestionId']})
			record_info["Total Question"]=len(question_data['Item']['question'])
			record_info['Question']=question_data['Item']['question']
			record_info['CurrentPostion'] = 0
			record_info['CurrentAnswerPostion'] = 0
			record_info['TestSeriesStatus'] = 0
			Record.put_item(Item = record_info)
			payload_data={
				'sessionId':event['SessionID'],
				'token':event['token'],
				'email':event['email'],
				'question_data':"You have already completed the test. To restart please say or write 'stop' the exit and start the test again.",
				"Current":0,
				'lastlogin':user_data['lastlogin'],
				'restart':"{ended}"
			}
			url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
			
			payload = json.dumps(payload_data, default=decimal_default)
			headers = {
			  'Content-Type': 'application/json'
			}
			response = requests.request("POST", url, headers=headers, data=payload)
			return {
				'statusCode': 200,
				'body': json.dumps('Hello from Lambda 1')
			}
	
	# if there is no record with given emailid and question id
	else:
		question_data = Question.get_item(Key={'id':event['id']})		
		updated_record_data={
			"userId":event['email'],
			"QuestionId":event['id'],
			"Token":event['token'],
			"Question":question_data['Item']['question'],
			"CurrentPostion":0,
			"Total Question":len(question_data['Item']['question']),
			"CorrectAnswerbyYou":0,
			"TestSeriesStatus":"Resume",
			"CurrentAnswerPostion":0
		}
		user_data['StartTestSeries']=True
		User.put_item(Item = user_data)
		Record.put_item(Item = updated_record_data)
		# CurrentPostion=updated_record_data["CurrentPostion"]
		payload_data={
			'sessionId':event['SessionID'],
			'email':event['email'],
			'token':event['token'],
			'question_data':updated_record_data['Question'][updated_record_data["CurrentPostion"]],
			"Current":1,
			'lastlogin':user_data['lastlogin'],
			'restart':"{Start}"
		}
		url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/InvestorUnsolicitedResponses"
		payload = json.dumps(payload_data, default=decimal_default)
		headers = {
		  'Content-Type': 'application/json'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		return {
			'statusCode': 200,
			'body': json.dumps('Hello from Lambda 2')
		}

def decimal_default(obj):
	if isinstance(obj, Decimal):
		return str(obj)
	raise TypeError