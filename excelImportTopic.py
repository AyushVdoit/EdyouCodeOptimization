import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
Topic=dynamodb.Table('Topic')
Token_Data = dynamodb.Table('Token')

# to verify token 
def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data :
		return True
	else:
		return False  

# to import topic from excel file
def lambda_handler(event, context):

	# ?no else statement for token checker 
	if token_checker(event['token']):
		data = event['data']
		data_copy = data
		missing_field_text = "The fields are missing at column "
		missing_fields_list = []
		count=1

		# check if all the fields are present in the input data
		for question in data_copy: 
			count+=1
			required_fields = ["Answer","QuestionVariation_1","QuestionVariation_2","QuestionVariation_3"]
			OptionsGiven={"Answer":"A","QuestionVariation_1":"B","QuestionVariation_2":"C","QuestionVariation_3":"D"}
			for field in required_fields:
				if field not in question or not question[field]:
					missing_fields_list.append(OptionsGiven[field]+str(count))
		
		# if fields are missing
		if len(missing_fields_list)>0:
			missing_fields_string = ', '.join(missing_fields_list)
			return {
				'statusCode': 400,
				'body': missing_field_text  + missing_fields_string
			}
		
		topic_data =Topic.get_item(Key={'Topic_id':event['Topic_id']})
		
		if 'Item' in topic_data:
			topic_dictionary=topic_data['Item']
			questions=topic_dictionary['question']
			# add question in questions field
			for each_question in data:
				descriptions = []
				for key in each_question:
					if key.startswith("QuestionVariation_"):
						if each_question[key]!="":
							descriptions.append({"subQ":each_question[key]})
				question={}
				question['Potential_Question']=descriptions
				question['correctAnswer']=each_question['Answer']+"7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup="
				question['qid']=uuid4().hex
				question['followup_status']=False
				question['prompt_status']=False
				question['followup']=""
				question['image']=""
				question['imageUrl']=""
				question['url']=""
				questions.append(question)
				topic_dictionary['question'] = questions
			Topic.put_item(Item=topic_dictionary)        
	
	return {
		'statusCode': 200,
		'body':"File Uploaded Succesfully"
	}
