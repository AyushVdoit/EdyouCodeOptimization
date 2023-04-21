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
import smtplib
import base64

s3 = boto3.client('s3')
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
		data = event
		required_fields = ["Topic_id","token","correctAnswer","Potential_Question"]

		# check if required fields are present in input data
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
			
		if token_checker(event['token']):
			topic_info =Topic.get_item(Key={'Topic_id':event['Topic_id']})
			if 'Item' in topic_info:
				topic_dictionary=topic_info['Item']
				topic_questions=topic_dictionary['question']
				topic={}

				# check if there are question variations
				for question in event["Potential_Question"]:
					if question["subQ"] is None:
						return {
							'statusCode': 400,
							'body': 'Question variations are required and cannot be empty'
							}
				
				uuid41=uuid4().hex

				# add image in s3 bucket and set image and image url
				bucket_name="pollydemo2022"
				object_key='images_dev/'+uuid41+'.jpg'
				if event['imageUrl'] !="" and event['imageUrl']!=None:   
					content_type = 'image/jpeg'
					image=event['imageUrl'].replace("data:image/png;base64,","")
					image = base64.b64decode(image)
					s3.put_object(Bucket=bucket_name, Key=object_key, Body=image, ContentType=content_type)
					event['image']="https://pollydemo2022.s3.us-west-2.amazonaws.com/"+object_key
					topic['image']=event['image']
					topic['imageUrl']=event['image']
				else:
					topic['image']=""
					topic['imageUrl']=""
				
				# set description
				if event['description']!="" and event['description']!=None :
					if event['prompt_status']==True or event['prompt_status']!=None:
						topic['description']= event['description']
					else:
						topic['description']=""
						event['prompt_status']=False
				else:
					topic['description']=""
				
				# set url and followup
				if event['url'] != "" and event['url']!=None:
					topic['url'] = event['url']
					if event['followup']!=""  and event['followup']!=None :
						if event['followup_status']:
							topic['followup']= event['followup']
						else:
							topic['followup']="click me"
					else:
						topic['followup']="click me"
				else:
					topic['url']=""
					topic['followup']= ""
		
				
				topic['correctAnswer']=event['correctAnswer']+"7481903939urlforyou="+topic['url']+"7581903939imagelinkforyou="+topic['image']+"7581904949Textlinkforyou="+topic['description']+"7581904949Followup="+topic['followup']
				topic['followup_status']=event['followup_status']
				# topic['correctAnswer']=event['correctAnswer']+"7481903939urlforyou="+topic['url']+"7581903939imagelinkforyou="+topic['image']+"7581904949Textlinkforyou="+topic['description']
				topic["Potential_Question"]=event['Potential_Question']
				topic['qid']=uuid41
				topic['description']=topic['description']
				topic['prompt_status']=event['prompt_status']
				topic_questions.append(topic)
				topic_dictionary['question'] = topic_questions
				Topic.put_item(Item=topic_dictionary)        
				return {
					'statusCode': 200,
					'body': "Topic ADDED"
				}
			else:
				return {
					'statusCode': 200,
					'body': 'No data found'
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