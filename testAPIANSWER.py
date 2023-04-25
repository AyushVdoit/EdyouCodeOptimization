import json
import openai
import os
import requests
import boto3
from decimal import Decimal
import urllib3
import re
import random
http = urllib3.PoolManager()
from boto3.dynamodb.conditions import Key
from difflib import SequenceMatcher

dynamodb = boto3.resource('dynamodb')
Question_Data = dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')
Record = dynamodb.Table("Record")
user = dynamodb.Table("user")

def api_call_util(data,gptPrompt):
	url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/openAIInvestor"
	payload = json.dumps({
		"data": data,
		"gptPrompt":gptPrompt
		
	})
	headers = {
		'Content-Type': 'application/json'
	}
	response = requests.request("POST", url, headers=headers, data=payload)
	return response.text

def response_data_util(options,answer):
	answer="".join(answer.split()).lower()
	for j in range(0,len(options)):
		i=options[j].split(" ")[1:]
		i="".join(i).lower()
		z=SequenceMatcher(a=answer,b=i).ratio()
		if z > .92:
			break    
	if j==len(options)-1:
		if z > .92:
			return j,True
		else:
			return False,False
	else:
		return j,True

def decimal_default(obj):
	if isinstance(obj, Decimal):
		return str(obj)
	raise TypeError

def lambda_handler(event, context):
	test_text = ""
	source_text = ""
	avatar=event['fm-avatar']
	avatar=json.loads(avatar)
	custom_data = event['fm-custom-data']
	custom_data=json.loads(custom_data)
	sid_token = event['sid']
	email = custom_data['email'] 
	dicinew={}
	# if type of avatar is welcome 
	if avatar['type']=="WELCOME":
		response_data="Hi "+ custom_data['name']+", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"
	# if type of avatar is question 
	else:
		user_data=user.get_item(Key={'email' : email})
		user_data=user_data['Item']
		# if no question received 
		if len(event['fm-question'])==0:
			response_data = "I didn't hear anything, please try again."
		elif event['fm-question'].lower() in ["show verbal commands","show verbal command","show available commands","call verbal commands","show me verbal commands","show marble command","to verbal commands","show border commands","show barbie commands"]:
			response_data = "The verbal commands that you can use <ul><li>Open test series page.</li><li>Open the dashboard.</li><li>Open my profile.</li><li>Please hide.</li><li>Please show yourself.</li><li>Display full screen.</li><li>Minimize the screen.</li><li>Enable my subtitles.</li><li>Disable subtitles.</li><li>Show your subtitles.</li><li>Hide your subtitles.</li><li>Show question.</li><li>Hide question.</li><li>Please logout.</li></ul>"
		elif event['fm-question'].lower() =='fine':
			response_data ="Great." 
		elif event['fm-question'].lower() =='stop':
			if user_data['StartTestSeries']==True:
				response_data ="Closing the quiz." 
				user_data['StartTestSeries']=False
				user.put_item(Item = user_data)
			else:
				response_data = "I didn't hear anything, please try again." 
		elif event['fm-question'].lower() =='i am here':
			response_data ="Ok, Good." 
		elif event['fm-question'].lower() =='no':
			if user_data['StartTestSeries']==True:
				response_data = "Ok. Take a break.<br>You can say 'Stop' to close the test."    
			else:
				response_data = "I didn't hear anything, please try again." 
		elif event['fm-question'].lower() =='repeat':
			# to repeat the question : return Question + options
			if user_data['StartTestSeries']==True:
				token_data_response = Token_Data.get_item(Key={'token' : sid_token})
				if 'QuestionId' in token_data_response['Item']:
					QID = token_data_response['Item']['QuestionId']
					record_data = Record.get_item(Key={'userId' :email,'QuestionId':QID})
					record_data = record_data['Item']
					CurrentPostion=record_data['CurrentPostion']
					CurrentPostion1=int(CurrentPostion)+1
					question_data = record_data['Question'][int(record_data['CurrentPostion'])]
					options = question_data["options"]
					Question = question_data["Question"]
					AC1 = "Question "+str(CurrentPostion1)+". "+Question 
					# html = "<ul>\n"
					html =""
					for option in options:
						html += f"{option}<br>\n"
					# html += "</ul>"
					# AC =str(CurrentPostion1)+". "+Question 
					dicinew = {
						"Question":AC1,
						"options":options,
						"Output":"",
						"Test":"",
						"text":AC1 + html
					}
					response_data =AC1 + html
				else:
					response_data = "Can you please repeat the sentence."
			else:
				response_data = "Can you repeat the question." 	
		elif event['fm-question'].lower() =='yes':
			if user_data['StartTestSeries']==True:
				token_data_response = Token_Data.get_item(Key={'token' : sid_token})
				if 'QuestionId' in token_data_response['Item']:
					QID = token_data_response['Item']['QuestionId']
					record_data = Record.get_item(Key={'userId' :email,'QuestionId':QID})
					record_data = record_data['Item']
					CurrentPostion=record_data['CurrentPostion']
					if CurrentPostion <=record_data['Total Question'] -1:
						CurrentPostion1=int(CurrentPostion)+1
						question_data = record_data['Question'][int(CurrentPostion)]
						options = question_data["options"]
						Question = question_data["Question"]
						AC1 ="Question "+str(CurrentPostion1)+". "+ Question 
						# html = "<ul>\n"
						html =""
						for option in options:
							html += f"{option}<br>\n"
						# html += "</ul>"
						response_data =AC1 + html
						
						dicinew = {
							"Question":AC1,
							"options":options,
							"Output":"",
							"Test":"",
							"text":response_data
						}
					else:
						record_data['CurrentPostion'] = 0
						record_data['CurrentAnswerPostion']=0
						record_data['TestSeriesStatus'] = 0
						question_data = Question_Data.get_item(Key={'id':QID})
						record_data["Total Question"]=len(question_data['Item']['question'])
						record_data['Question']=question_data['Item']['question']
						Record.put_item(Item = record_data)
						response_data="The test is completed. Please say or write 'Stop' to exit."
				else:
					response_data = "Can you please repeat the sentence."
			else:
				response_data = "Can you repeat the question." 
		else:
			token_data_response = Token_Data.get_item(Key={'token' : sid_token})
			if 'QuestionId' in token_data_response['Item']:
				QID = token_data_response['Item']['QuestionId']
				record_data = Record.get_item(Key={'userId' :email,'QuestionId':QID})
				record_data = record_data['Item']
			else:
				record_data={}
			if "Question" in record_data:
				if int(record_data['Total Question']) == int(record_data['CurrentPostion']):
					value = False
				else:
					answerdata,value= response_data_util(record_data['Question'][int(record_data['CurrentPostion'])]['options'],event["fm-question"])
			else:
				value=False
			l=[]
			if value ==False:
				url="http://52.11.66.129:5002/webhooks/rest/webhook"
				# url ="http://35.91.228.35:5002/webhooks/rest/webhook"
				encoded_data = json.dumps({  "sender": "adarsh","message": event["fm-question"]})
				resp = http.request('POST',url,body=encoded_data,headers={'Content-Type': 'application/json'})
				data=json.loads(resp.data.decode('utf-8'))
				if len(data)==0:
					if user_data["gpt3"]==True:
						data_from_openAI=api_call_util(event["fm-question"],user_data['gptPromptUser'])
						if (('errorMessage' in data_from_openAI) or ('statusCode' in data_from_openAI)):
							random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
							random_number_no_response  =random.randint(0,len(random_no_response)-1)
							response_data=random_no_response[random_number_no_response]
						else:
							response_data=data_from_openAI
							# output_string = re.sub(r"[\n•●○\-]+\s*", "<br>", response_data)
							# # Detect if list is ordered or unordered
							# list_type = "unordered"
							# if re.search(r"<br>\d+\. ", output_string):
							#     list_type = "ordered"
				
							# # Replace bullet points with HTML list tags
							# if list_type == "unordered":
							#     output_string = re.sub(r"(?:<br>)+- ", "<ul><li>", output_string)
							#     output_string = re.sub(r"(?:<br>)+", "</li><li>", output_string)
							#     output_string = re.sub(r"(?:<li>.+)</li>", "<li>\\g<0></li></ul>", output_string)
							# elif list_type == "ordered":
							#     output_string = re.sub(r"<br>(\d+)\. ", "<ol start='\\1'><li>", output_string)
							#     output_string = re.sub(r"<br>", "</li><li>", output_string)
							#     output_string = re.sub(r"(?:<li>.+)</li>", "<li>\\g<0></li></ol>", output_string)
							
							# # Replace consecutive "<br>" tags with just one
							# output_string = re.sub(r"<br>{2,}", "<br>", output_string)
						
							# print(output_string)
							# response_data=output_string
							source_text ="<br>Source: OpenAI" 
					else:
						random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
						random_number_no_response  =random.randint(0,len(random_no_response)-1)
						response_data=random_no_response[random_number_no_response]
						
				for i in range(0,len(data)):
					response_data=data[i]['text']
					
					if response_data in ['0','1','2','3','4']:
						if user_data['StartTestSeries']==True:
							description=record_data['Question'][int(record_data['CurrentPostion'])]['description']
							response_data=int(response_data)
							# question11=record_data['Question'][int(record_data['CurrentPostion'])]['Question']
							options = record_data['Question'][int(record_data['CurrentPostion'])]['options']
							dicinew={
								"options":options
							}
							correctPostioin =int(record_data['Question'][int(record_data['CurrentPostion'])]['correctPostioin'])
							if response_data == correctPostioin:
								record_data['CorrectAnswerbyYou']=record_data['CorrectAnswerbyYou']+1
								record_data['CurrentAnswerPostion']=record_data['CurrentAnswerPostion']+1
								record_data['CurrentPostion']=record_data['CurrentPostion']+1
								record_data['TestSeriesStatus'] ="Resume"
								gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
								random_number1  =random.randint(0,len(gesture)-1)
								l.append(gesture[random_number1]+description[response_data])
								# l.append(description[response_data])
								
								l.append("<br><br>Shall we move to the next question?")
								response_data = ' '.join(l)
								test_text = "Test"
								# response_data = l
								Record.put_item(Item = record_data)
							else:
								response_data=description[response_data]
								gesture  = ["Alas! ","Nice try but ","Too bad, ","Good attempt but "]
								random_number1  =random.randint(0,len(gesture)-1)
								l.append(gesture[random_number1]+response_data)
								
								# l.append(response_data)
								l.append("<br>The correct Answer is - ")
								correctAnswer = record_data['Question'][int(record_data['CurrentPostion'])]['correctAnswer']
								correctAnswer = correctAnswer[3:] 
								correctAnswer = correctAnswer.split('.')[0]
								l.append('"'+correctAnswer+'".')
								record_data['CurrentAnswerPostion']=record_data['CurrentAnswerPostion']+1
								record_data['CurrentPostion']=record_data['CurrentPostion']+1
								record_data['TestSeriesStatus'] ="Resume"
								Record.put_item(Item = record_data)
								l.append("<br><br>Shall we move to the next question?")
								response_data = ' '.join(l)
								test_text = "Test"
								# response_data = l
						else:
							response_data = "Can you repeat the question." 
					else:
						if response_data =='repeat':
							if user_data['StartTestSeries']==True:
								response_data,dicinew =get_question_html(record_data)
							else:
								response_data = "Can you repeat the question." 
						elif response_data =='yes':
							if user_data['StartTestSeries']==True:
								response_data,dicinew  = get_next_question_html(sid_token,email) 
							else:
								response_data = "Can you repeat the question."
						elif response_data =='stop':
							if user_data['StartTestSeries']==True:                      
								response_data ="Closing the quiz." 
								user_data['StartTestSeries']=False
								user.put_item(Item = user_data)
							else:
								response_data ="stop" 
						else:
							l.append(response_data)
							# l.append('<br>')
							response_data = ' '.join(l) 
							# response_data = l

			else:
				correctPostioin =int(record_data['Question'][int(record_data['CurrentPostion'])]['correctPostioin'])
				description = record_data['Question'][int(record_data['CurrentPostion'])]['description']
				options = record_data['Question'][int(record_data['CurrentPostion'])]['options']
				dicinew={
					"options":options
				}
				
				if answerdata == correctPostioin:
					record_data['CorrectAnswerbyYou']=record_data['CorrectAnswerbyYou']+1
					record_data['CurrentAnswerPostion'] =record_data['CurrentAnswerPostion']+1
					record_data['CurrentPostion']=record_data['CurrentPostion']+1
					record_data['TestSeriesStatus'] ="Resume"
					gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
					random_number1  =random.randint(0,len(gesture)-1)
					l.append(gesture[random_number1]+description[answerdata])
					# l.append(description[answerdata])
					l.append("<br><br>Shall we move to the next question?")
					response_data = ' '.join(l)
					test_text = "Test"

					# response_data = l
					Record.put_item(Item = record_data)
				else:
					response_data=description[answerdata]
					gesture  = ["Alas! ","Nice try but ","Too bad, ","Good attempt but "]
					random_number1  =random.randint(0,len(gesture)-1)
					l.append(gesture[random_number1]+response_data)       
					# l.append(response_data)
					l.append("<br>The correct Answer is - ")
					correctAnswer = record_data['Question'][int(record_data['CurrentPostion'])]['correctAnswer']
					correctAnswer = correctAnswer[3:]
					correctAnswer = correctAnswer.split('.')[0]
					l.append('"'+correctAnswer+'".')
					record_data['CurrentAnswerPostion'] =record_data['CurrentAnswerPostion']+1
					record_data['CurrentPostion']=record_data['CurrentPostion']+1
					record_data['TestSeriesStatus'] ="Resume"
					Record.put_item(Item = record_data)
					l.append("<br><br>Shall we move to the next question?")
					response_data = ' '.join(l)
					test_text = "Test"

					# response_data = l
	# response_data =json.dumps(response_data)
	# data2 = response_data.replace("<br>","")
	data2 = response_data
	data4 = data2
	if source_text !="":
		if response_data[0]=='"':
			response_data=response_data[1:]
			if response_data[-1]=='"':
				response_data=response_data[:-1]
				if response_data[0]=="?":
					response_data=response_data[1:]
				else:
					pass
			else:
				pass
		else:
			pass
		response_data = str(response_data + source_text)
		print(response_data) 
	data4 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+data2+'</mstts:express-as></voice></speak>'    
	if "options" in dicinew:
		if "Question" in dicinew:
			pass
		else:
			dicinew['Question']=""
			if test_text =="":
				dicinew['Output'] = response_data.replace("e-dee-YOU","edYOU")
				dicinew['Test']=test_text
				dicinew['text']=data2
			else:    
				dicinew['Output'] = ""
				dicinew['Test']=response_data
				dicinew['text']=data2        
	else:
		dicinew['Question']=""
		# if type(response_data) ==list:
			# response_data = ' '.join(response_data)
		dicinew['options']=[]
		if test_text =="":
			dicinew['Output'] = response_data.replace("e-dee-YOU","edYOU")
			dicinew['Test']=test_text
			dicinew['text']=data2
		else:    
			dicinew['Output'] = ""
			dicinew['Test']=response_data
			dicinew['text']=data2
		# else:
		#     dicinew['options']=[response_data]
	instructions = {
		"customData": dicinew
	}
	
	# dici={'answer':response_data,"instructions":json.dumps(instructions, separators=(',', ':'), ensure_ascii=False)}  
	dici = {'answer':data4,"instructions":instructions}
	print(dici)
	# dici = {'answer':response_data}
	return{
		'answer':json.dumps(dici),
		"matchedContext": "",
		"conversationPayload": "{}"
	}


	
def is_json(my_json):
	try:
		json_object = json.loads(my_json)
	except ValueError:
		return False
	return True

def get_question_html(record_data):
	question_data = record_data['Question'][int(record_data['CurrentPostion'])]
	CurrentPostion = record_data['CurrentPostion']
	CurrentPostion1 = int(CurrentPostion)+1
	options = question_data["options"]
	Question = question_data["Question"]
	AC ="Question "+str(CurrentPostion1)+". "+Question 
	# html = "<ul>\n"
	html=""
	for option in options:
		html += f"{option}<br>\n"
	# html += "</ul>"
	data = AC + html
	dicinew = {
		"Question":AC,
		"options":options,
		"Output":"",
		"Test":"",
		"text":data
	}
	# dici=json.dumps(dicinew)
	# response_data = dici
	# return AC + html
	# return response_data
	return data,dicinew


def get_next_question_html(sid_token, email):
	token_data_response = Token_Data.get_item(Key={'token': sid_token})
	if 'QuestionId' in token_data_response['Item']:
		QID = token_data_response['Item']['QuestionId']
		record_data = Record.get_item(Key={'userId': email, 'QuestionId': QID})
		record_data = record_data['Item']
		CurrentPostion = record_data['CurrentPostion']
		if CurrentPostion <= record_data['Total Question']-1:
			CurrentPostion1 = int(CurrentPostion)+1
			question_data = record_data['Question'][int(record_data['CurrentPostion'])]
			options = question_data["options"]
			Question = question_data["Question"]
			AC ="Question "+str(CurrentPostion1)+". "+ Question
			# html = "<ul>\n"
			html =""
			for option in options:
				html += f"{option}<br>\n"
				# html += "</ul>"
			data = AC + html
			# AC =str(CurrentPostion1)+". "+Question 
			dicinew = {
				"Question":AC,
				"options":options,
				"Output":"",
				"Test":"",
				"text":data
			}
			return data,dicinew
		else:
			record_data['CurrentPostion'] = 0
			record_data['CurrentAnswerPostion']= 0
			record_data['TestSeriesStatus'] = 0
			Record.put_item(Item=record_data)
			return "The test is complete. Please say or write 'Stop' to exit.",{}
	else:
		return "Please start the test first.",{}


