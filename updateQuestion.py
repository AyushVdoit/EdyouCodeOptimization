import json
import boto3
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data=Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  
	
# to update the question with qid 
def lambda_handler(event, context):
	try:
		data =event
		required_fields = ["id","token","qid","correctAnswer","description","options","Question"]
		for field in required_fields:
			if field not in data or not data[field]:
				return {
				'statusCode': 400,
				'body': f'Error: {field} is required and cannot be empty'
				}
		if token_checker(event['token']):
			questions =Question.get_item(Key={'id':event["id"]})
			if 'Item' in questions:
				question_info=questions['Item']
				stored_questions=question_info['question']
				question={}
				question['qid']=event['qid']    
				letters = ["A.", "B.", "C.", "D.", "E."]
				new_value  = {"Option A":0,"Option B":1,"Option C":2,"Option D":3,"Option E":4}
				options=event['options']
				new_options = []
				for i, option in enumerate(options):
					new_option = f"{letters[i]} {option}"
					new_options.append(new_option)
				correct_answer_position = new_value[event['correctAnswer']]
				replacements  = {0:"A",1: "B",2:"C",3:"D",4:"E"}
				question['correctAnswer']=letters[correct_answer_position]+" "+options[correct_answer_position]
				question['correctPostioin'] = correct_answer_position
				question['correctAnswerFrontend'] = event['correctAnswer']
				question["options"]=new_options
				description = event['description']
				if 'hint' in event:
					question['hint'] = event['hint']
				else:
					question['hint'] = ""
				for i, desc in enumerate(description):
					if i == correct_answer_position:
						description[i] = replacements[i]+" is correct because "+description[i]
					else:
						description[i] = replacements[i]+" is incorrect because "+description[i]
	
				question['description']=description
				
				question["Question"]=event['Question']
				
				
				
				
				
				index = next((i for i, q in enumerate(stored_questions) if q['qid'] == event['qid']), None)
				if index is not None:
					stored_questions[index] = question
					question_info['question'] = stored_questions
					Question.put_item(Item=question_info)
					return {
						'statusCode': 200,
						'body': "Question Updated Succesfully"
					}
				else:
				
					return {
					'statusCode': 200,
					'body': 'No item Found'
					}

				

			else:
				
				return {
				'statusCode': 200,
				'body': 'No item Found'
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
