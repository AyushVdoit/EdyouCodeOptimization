import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

# to verify the token
def token_checker(token):
	data = Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  

def lambda_handler(event, context):
	if token_checker(event['token']):
		data = event['data']
		data_copy = data
		missing_field_text = "The fields are missing at column "
		missing_field_list =[]
		count=1

		# check if all the fields are present in the input data
		for question in data_copy: 
			count+=1
			required_fields = ["correctAnswer","description__001","description__002","description__003","description__004","description__005","options__001","options__002","options__003","options__004","options__005","Question","hint"]
			options_given = {'correctAnswer': 'A','description__001': 'B','description__002': 'C','description__003': 'D','description__004': 'E','description__005': 'F','options__001': 'G','options__002': 'H','options__003': 'I','options__004': 'J','options__005': 'K','Question': 'L','hint': 'M'}
			for field in required_fields:
				if field not in question or not question[field]:
					missing_field_list.append(options_given[field]+str(count))
					
		# if any field from required field is missing
		if len(missing_field_list)>0:         
			string = ', '.join(missing_field_list)
			return {
				'statusCode': 400,
				'body': missing_field_text + string
			}
		
		question_data = Question.get_item(Key={'id':event['id']})
		if 'Item' in question_data:
			question_dictionary=question_data['Item']
			questions=question_dictionary['question']
			# add input questions in the question field
			for each_question in data:
				descriptions = []
				options = []
				for key in each_question:
					if key.startswith("description__"):
						descriptions.append(each_question[key])
					elif key.startswith("options__"):
						options.append(each_question[key])
				question={}
				letters = ["A.", "B.", "C.", "D.", "E."]
				new_options = []
				for i, option in enumerate(options):
					new_option = f"{letters[i]} {option}"
					new_options.append(new_option)

				# convert options to lowercase 
				lowercase_options = [s.lower() for s in options]
				correct_answer_position = lowercase_options.index(each_question['correctAnswer'].lower())
				replacements  = {0:"A",1: "B",2:"C",3:"D",4:"E"}
				new_value  = {0:"Option A",1:"Option B",2:"Option C",3:"Option D",4:"Option E"}
				question['correctAnswer']=letters[correct_answer_position]+" "+options[correct_answer_position]

				# ?it should be position instead of Postioin
				question['correctPostioin'] = correct_answer_position
				question["options"]=new_options
				if 'hint' in each_question:
					question['hint'] = each_question['hint']
				else:
					question['hint'] = ""
				for i, desc in enumerate(descriptions):
					if i == correct_answer_position:
						descriptions[i] = replacements[i]+" is correct because "+descriptions[i]
					else:
						descriptions[i] = replacements[i]+" is incorrect because "+descriptions[i]
	
				question['description']=descriptions
				question['correctAnswerFrontend'] = new_value[correct_answer_position]

				question["Question"]=each_question['Question']
				question['qid']=uuid4().hex
				questions.append(question)
				question_dictionary['question'] = questions
			Question.put_item(Item=question_dictionary)        
			return {
					'statusCode': 200,
					'body': "File Uploaded Succesfully"
				}
	
