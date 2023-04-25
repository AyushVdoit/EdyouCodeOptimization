import json
import os
import requests
import boto3
from decimal import Decimal
import urllib3
import re
import random
http = urllib3.PoolManager()
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
Question_Data = dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')
Record = dynamodb.Table("Record")
user = dynamodb.Table("Investor")
Investor_Login_History = dynamodb.Table("InvestorLoginHistory")

from difflib import SequenceMatcher
def api_call_util(data,gptPrompt):
	url = "https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Development/crudInvestor/openAIInvestor"
	# url="https://1i4zp3969d.execute-api.us-west-2.amazonaws.com/Production/openAI/request"
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


def check_key(key, dictionary_list):
	for dictionary in dictionary_list:
		if key in dictionary:
			return True
	return False

def decimal_default(obj):
	if isinstance(obj, Decimal):
		return str(obj)
	raise TypeError

def lambda_handler(event, context):
	test_text = ""	  # "Test"
	source_text = ""  # "<br>Source: OpenAI" 
	dicinew={}
	avatar=event['fm-avatar']
	avatar=json.loads(avatar)
	custom_data = event['fm-custom-data']
	custom_data=json.loads(custom_data)
	sid_token = event['sid']
	email = custom_data['email']
	prompt = custom_data['prompt']
	time = custom_data['time']
	investor_login_history_info = Investor_Login_History.get_item(Key={'email' :email,'time':time})
	investor_login_history_info = investor_login_history_info['Item']
	investor_login_history_data = investor_login_history_info['data']
	user_data=user.get_item(Key={'email' : email})
	user_data=user_data['Item']

	if email=="statefarm@edyou.com":
		# if type is welcome
		if avatar['type']=="WELCOME":
			response_data = prompt
			link,imageUrl,textaddon,followup="","","",""
			new_log_data={"user":"{Initialise}","bot":response_data}
			investor_login_history_data.append(new_log_data)
			investor_login_history_info['data'] =investor_login_history_data
			Investor_Login_History.put_item(Item=investor_login_history_info)  
		# if type is question
		else:
			# frequent cases handled 
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
					response_data="Ok."
					# response_data = "why you say no, be positive say yes always" 
			elif event['fm-question'].lower() =='repeat':
				# to repeat test series
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
						record_data = record_data['Item']
						CurrentPostion=record_data['CurrentPostion']
						CurrentPostion1=int(CurrentPostion)+1
						question_data = record_data['Question'][int(record_data['CurrentPostion'])]
						options = question_data["options"]
						Question = question_data["Question"]
						AC1 = "Question "+str(CurrentPostion1)+". "+Question 
						html =""
						for option in options:
							html += f"{option}<br>\n"
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
					# response_data = "You cannot hear at once, It's to hard to repeat for me send me $5 for repeating my self" 
					response_data="Ok."            
			elif event['fm-question'].lower() in ['show options','show option','show answers','show answer','options','option']:
				# for test series to only show options
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
						record_data = record_data['Item']
						CurrentPostion=record_data['CurrentPostion']
						CurrentPostion1=int(CurrentPostion)+1
						question_data = record_data['Question'][int(record_data['CurrentPostion'])]
						options = question_data["options"]
						html =""
						for option in options:
							html += f"{option}<br>\n"
						response_data =html
					else:
						response_data = "Can you please repeat the sentence."
				else:
					response_data = "Ok." 
			elif event['fm-question'].lower() =='yes':
				# for test series 
				# ? which case is handled here 
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
						record_data = record_data['Item']
						CurrentPostion=record_data['CurrentPostion']
						# if current question is not last question of test series 
						if CurrentPostion <=record_data['Total Question'] -1:
							CurrentPostion1=int(CurrentPostion)+1
							question_data = record_data['Question'][int(CurrentPostion)]
							options = question_data["options"]
							question_text = question_data["Question"]
							AC1 ="Question "+str(CurrentPostion1)+". "+ question_text 
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
							# if current question is last question
							record_data['CurrentPostion'] = 0
							record_data['CurrentAnswerPostion']=0
							record_data['TestSeriesStatus'] = 0
							question_data = Question_Data.get_item(Key={'id':question_id})
							record_data["Total Question"]=len(question_data['Item']['question'])
							record_data['Question']=question_data['Item']['question']
							Record.put_item(Item = record_data)
							response_data="The test is completed. Please say or write 'Stop' to exit."
					else:
						response_data = "Can you please repeat the sentence."
				else:
					response_data = "Ok." 		
			# if question does not match with manually handled cases 
			else:
				token_data_response = Token_Data.get_item(Key={'token' : sid_token})
				# if there is questionid in token data 
				if 'QuestionId' in token_data_response['Item']:
					question_id = token_data_response['Item']['QuestionId']
					record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
					record_data = record_data['Item']
				else:
					record_data={}
				# if there is question in record 
				if "Question" in record_data:
					# if current question is last question 
					if int(record_data['Total Question']) == int(record_data['CurrentPostion']):
						value = False
					else:
						# answer_data gives the index of option , and value gives true/false 
						answer_data,value= response_data_util(record_data['Question'][int(record_data['CurrentPostion'])]['options'],event["fm-question"])
				else:
					value=False
				l=[]
				# ? what is the meaning of value 
				if value ==False:
					url ="http://52.11.66.129:5002/webhooks/rest/webhook"
					# url ="http://35.91.228.35:5002/webhooks/rest/webhook"
					encoded_data = json.dumps({  "sender": "adarsh","message": event["fm-question"]})
					resp = http.request('POST',url,body=encoded_data,headers={'Content-Type': 'application/json'})
					data=json.loads(resp.data.decode('utf-8'))
					# if there is no response text
					if len(data)==0:
						# if user has access to chat gpt 
						if user_data["gpt3"]==True:
							data_from_openAI=api_call_util(event["fm-question"],user_data['gptPrompt'])
							# if there is error in api call 
							if (('errorMessage' in data_from_openAI) or ('statusCode' in data_from_openAI)):
								random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
								random_number_no_response  =random.randint(0,len(random_no_response)-1)
								response_data=random_no_response[random_number_no_response]
							else:
								# response data will be response from openAI
								response_data=data_from_openAI
								source_text ="<br>Source: OpenAI" 
						else:
							# if user do not have access to chat gpt
							random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
							random_number_no_response  =random.randint(0,len(random_no_response)-1)
							response_data=random_no_response[random_number_no_response]

					# if there is response data 	
					for i in range(0,len(data)):
						response_data=data[i]['text']
						if response_data in ['07481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','17481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','27481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','37481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','47481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=']:
							# for test series 
							if user_data['StartTestSeries']==True:
								description=record_data['Question'][int(record_data['CurrentPostion'])]['description']
								# get response data option from user 
								response_data=int(linkandtextSeprationText(response_data))
								options = record_data['Question'][int(record_data['CurrentPostion'])]['options']
								dicinew={
									"options":options
								}
								correctPostioin =int(record_data['Question'][int(record_data['CurrentPostion'])]['correctPostioin'])
								# if answer is correct 
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
									# update record data and move to next question 
									Record.put_item(Item = record_data)
								# if answer is wrong
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
								response_data = "Ok." 
						else:
							if response_data =='repeat7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
								if user_data['StartTestSeries']==True:
									response_data,dicinew =get_question_html(record_data)
								else:
									response_data = "Ok." 
							elif response_data =='yes7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
								if user_data['StartTestSeries']==True:
									response_data,dicinew  = get_next_question_html(sid_token,email) 
								else:
									response_data = "Ok."
							elif response_data =='stop7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
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
				
				# if value is true
				else:
					correctPostioin =int(record_data['Question'][int(record_data['CurrentPostion'])]['correctPostioin'])
					description = record_data['Question'][int(record_data['CurrentPostion'])]['description']
					options = record_data['Question'][int(record_data['CurrentPostion'])]['options']
					dicinew={
						"options":options
					}
					
					if answer_data == correctPostioin:
						record_data['CorrectAnswerbyYou']=record_data['CorrectAnswerbyYou']+1
						record_data['CurrentAnswerPostion'] =record_data['CurrentAnswerPostion']+1
						record_data['CurrentPostion']=record_data['CurrentPostion']+1
						record_data['TestSeriesStatus'] ="Resume"
						gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
						random_number1  =random.randint(0,len(gesture)-1)
						l.append(gesture[random_number1]+description[answer_data])
						# l.append(description[answer_data])
						l.append("<br><br>Shall we move to the next question?")
						response_data = ' '.join(l)
						test_text = "Test"
	
						# response_data = l
						Record.put_item(Item = record_data)
					else:
						response_data=description[answer_data]
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
			response_data,link,imageUrl,textaddon,followup=linkandtextSepration(response_data)
			new_log_data={"user":event["fm-question"],"bot":response_data}
			investor_login_history_data.append(new_log_data)
			investor_login_history_info['data'] =investor_login_history_data
			Investor_Login_History.put_item(Item=investor_login_history_info)
	# if email is not statefarm 
	else:
		if avatar['type']=="WELCOME":
			# response_data="Hi "+ custom_data['name']+", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"
			response_data = prompt
			link,imageUrl,textaddon,followup="","","",""
			# response_data,link,imageUrl,textaddon,followup=linkandtextSepration(response_data)
			new_log_data={"user":"{Initialise}","bot":response_data}
			# new_log_data={"bot":response_data}
			investor_login_history_data.append(new_log_data)
			investor_login_history_info['data'] =investor_login_history_data
			Investor_Login_History.put_item(Item=investor_login_history_info)
			# if user_data['firstTime']:
			#     user_data['firstTime']=False
			#     user.put_item(Item=user_data)
			# else:
			#     pass
			# textaddon="""<p>Ask me:</p>
			#             <ul>
			#             <li>What is edYOU?</li>
			#             <li>What markets does edYOU serve?</li>
			#             <li>How does edYOU make money?</li>
			#             <li>What is different about edYOU?</li>
			#             <li>What is the roadmap of edYOU?</li>
			#             <li>What is the history and progress of edYOU?</li>
			#             <li>Tell me more about you Hannah</li>
			#             <li>Can you show me a demo?</li>
			#             <li>What are the benefits of edYOU?</li>
			#             <li>How do I schedule a follow-up call?</li>
			#             </ul>"""    
		else:
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
					response_data="Ok."
					# response_data = "why you say no, be positive say yes always" 
			elif event['fm-question'].lower() =='repeat':
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
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
					# response_data = "You cannot hear at once, It's to hard to repeat for me send me $5 for repeating my self" 
					response_data="Ok."            
			elif event['fm-question'].lower() in ['show options','show option','show answers','show answer','options','option']:
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
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
						response_data =html
					else:
						response_data = "Can you please repeat the sentence."
				else:
					response_data = "Ok." 	
			elif event['fm-question'].lower() =='yes':
				if user_data['StartTestSeries']==True:
					token_data_response = Token_Data.get_item(Key={'token' : sid_token})
					if 'QuestionId' in token_data_response['Item']:
						question_id = token_data_response['Item']['QuestionId']
						record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
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
							question_data = Question_Data.get_item(Key={'id':question_id})
							record_data["Total Question"]=len(question_data['Item']['question'])
							record_data['Question']=question_data['Item']['question']
							Record.put_item(Item = record_data)
							response_data="The test is completed. Please say or write 'Stop' to exit."
					else:
						response_data = "Can you please repeat the sentence."
				else:
					response_data = "Ok." 
			else:
				token_data_response = Token_Data.get_item(Key={'token' : sid_token})
				if 'QuestionId' in token_data_response['Item']:
					question_id = token_data_response['Item']['QuestionId']
					record_data = Record.get_item(Key={'userId' :email,'QuestionId':question_id})
					record_data = record_data['Item']
				else:
					record_data={}
				if "Question" in record_data:
					if int(record_data['Total Question']) == int(record_data['CurrentPostion']):
						value = False
					else:
						answer_data,value= response_data_util(record_data['Question'][int(record_data['CurrentPostion'])]['options'],event["fm-question"])
				else:
					value=False
				l=[]
				if value ==False:
					url ="http://54.191.88.2:5005/webhooks/rest/webhook"
					# url="http://52.11.66.129:5002/webhooks/rest/webhook"
					# url ="http://35.91.228.35:5002/webhooks/rest/webhook"
					encoded_data = json.dumps({  "sender": "adarsh","message": event["fm-question"]})
					resp = http.request('POST',url,body=encoded_data,headers={'Content-Type': 'application/json'})
					data=json.loads(resp.data.decode('utf-8'))
					print(data)
					if len(data)==0:
						if user_data["gpt3"]==True:
							data_from_openAI=api_call_util(event["fm-question"],user_data['gptPrompt'])
							if (('errorMessage' in data_from_openAI) or ('statusCode' in data_from_openAI)):
								random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
								random_number_no_response  =random.randint(0,len(random_no_response)-1)
								response_data=random_no_response[random_number_no_response]
							else:
								response_data=data_from_openAI
								source_text ="<br>Source: OpenAI" 
						else:
							random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
							random_number_no_response  =random.randint(0,len(random_no_response)-1)
							response_data=random_no_response[random_number_no_response]
							
					for i in range(0,len(data)):
						response_data=data[i]['text']
						
						if response_data in ['07481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','17481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','27481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','37481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','47481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=']:
							if user_data['StartTestSeries']==True:
								description=record_data['Question'][int(record_data['CurrentPostion'])]['description']
								response_data=int(linkandtextSeprationText(response_data))
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
								response_data = "Ok." 
						else:
							if response_data =='repeat7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
								if user_data['StartTestSeries']==True:
									response_data,dicinew =get_question_html(record_data)
								else:
									response_data = "Ok." 
							elif response_data =='yes7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
								if user_data['StartTestSeries']==True:
									response_data,dicinew  = get_next_question_html(sid_token,email) 
								else:
									response_data = "Ok."
							elif response_data =='stop7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
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
					
					if answer_data == correctPostioin:
						record_data['CorrectAnswerbyYou']=record_data['CorrectAnswerbyYou']+1
						record_data['CurrentAnswerPostion'] =record_data['CurrentAnswerPostion']+1
						record_data['CurrentPostion']=record_data['CurrentPostion']+1
						record_data['TestSeriesStatus'] ="Resume"
						gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
						random_number1  =random.randint(0,len(gesture)-1)
						l.append(gesture[random_number1]+description[answer_data])
						# l.append(description[answer_data])
						l.append("<br><br>Shall we move to the next question?")
						response_data = ' '.join(l)
						test_text = "Test"
	
						# response_data = l
						Record.put_item(Item = record_data)
					else:
						response_data=description[answer_data]
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
			response_data,link,imageUrl,textaddon,followup=linkandtextSepration(response_data)
			new_log_data={"user":event["fm-question"],"bot":response_data}
			investor_login_history_data.append(new_log_data)
			investor_login_history_info['data'] =investor_login_history_data
			Investor_Login_History.put_item(Item=investor_login_history_info)
	

	final_response_data = response_data
	if source_text !="":
		if response_data[0]=='"':
			response_data=response_data[1:]
			if response_data[-1]=='"':
				response_data=response_data[:-1]
		response_data = str(response_data + source_text)
	replaced_response_data=final_response_data.replace('edYOU','e-dee-you')
	# final_response_data=final_response_data.replace('edu','e-dee-you')
	answer_data_text = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+replaced_response_data+'</mstts:express-as></voice></speak>'
	dicinew['description']=textaddon
	dicinew['link']=link
	dicinew['imageUrl']=imageUrl
	dicinew['followup']=followup
	if "options" in dicinew:
		if "Question" in dicinew:
			pass
		else:
			dicinew['Question']=""
			if test_text =="":
				dicinew['Output'] = response_data
				dicinew['Test']=test_text
				dicinew['text']=final_response_data
			else:    
				dicinew['Output'] = ""
				dicinew['Test']=response_data
				dicinew['text']=final_response_data        
	else:
		dicinew['Question']=""
		# if type(response_data) ==list:
			# response_data = ' '.join(response_data)
		dicinew['options']=[]
		if test_text =="":
			dicinew['Output'] = response_data
			dicinew['Test']=test_text
			dicinew['text']=final_response_data
		else:    
			dicinew['Output'] = ""
			dicinew['Test']=response_data
			dicinew['text']=final_response_data
		# else:
		#     dicinew['options']=[response_data]
	instructions = {
		"customData": dicinew
	}
	
	dici = {'answer':answer_data_text,"instructions":instructions}
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
		question_id = token_data_response['Item']['QuestionId']
		record_data = Record.get_item(Key={'userId': email, 'QuestionId': question_id})
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


# def linkandtextSepration(string):
#     text=string.split("7481903939")[0]
#     url=string.split("7581903939")[0]
#     url=url.split("7481903939urlforyou=")
#     if len(url)==2:
#         url=url[1]
#     else:
#         url=""
#     urlImage=string.split("7581903939imagelinkforyou=")
#     if len(urlImage)==2:
#         urlImage=urlImage[1]
#     else:
#         urlImage=""
#     return(text,url,urlImage)
	
# def linkandtextSepration(string):
#     text=string.split("7481903939")[0]
#     url=string.split("7581903939")[0]
#     url=url.split("7481903939urlforyou=")
#     if len(url)==2:
#         url=url[1]
#     else:
#         url=""
#     urlImage=string.split("7581903939imagelinkforyou=")
#     print(urlImage)
#     if len(urlImage)==2:
#         urlImage=urlImage[1].split("7581904949Textlinkforyou=")[0]
#     else:
#         urlImage=""
#     urlDescription=string.split("7581904949Textlinkforyou=")
#     if len(urlDescription)==2:
#         urlDescription=urlDescription[1]
#     else:
#         urlDescription=""

def linkandtextSeprationText(string):
	text=string.split("7481903939")[0]
	return text


def linkandtextSepration(string):
	text=string.split("7481903939")[0]
	url=string.split("7581903939")[0]
	url=url.split("7481903939urlforyou=")
	if len(url)==2:
		url=url[1]
	else:
		url=""
	urlImage=string.split("7581903939imagelinkforyou=")
	# print(urlImage)
	if len(urlImage)==2:
		urlImage=urlImage[1].split("7581904949Textlinkforyou=")[0]
	else:
		urlImage=""
	urlDescription=string.split("7581904949Textlinkforyou=")
	if len(urlDescription)==2:
		data=urlDescription[1].split("7581904949Followup=")
		urlDescription=data[0]
		if len(data)==2:
			followup=data[1]
		else:
			followup=""
	else:
		urlDescription=""
		followup=""
	return(text,url,urlImage,urlDescription,followup)