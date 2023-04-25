import json
# import openai
import os
import requests
import boto3
from decimal import Decimal
import urllib3
import re
import random
import pprint;

http = urllib3.PoolManager()
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Question_Data = dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')
Record = dynamodb.Table("Record")
user = dynamodb.Table("Investor")
InvestorLoginHistory = dynamodb.Table("InvestorLoginHistory")

from difflib import SequenceMatcher
def APICall(data,gptPrompt):
	print("APICall gptPrompt: " + gptPrompt + "\n")
	# setting gptPrompt null just in case something is sent
	# switching the below
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
	print("APICall response: ")
	print(response)
	return response.text

def ResponseData(options,answer):
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
	print("-------------------------------------- in lambda_handler() -----------------------------------\n")
	data3 = ""
	test1 = ""
	dicinew={}
	#print("lambda_handler event: " 
	# print(event) #doesn't work
	avatar=event['fm-avatar']
	avatar=json.loads(avatar)
	Custom = event['fm-custom-data']
	Custom=json.loads(Custom)
	# print("Custom: ")
	# pprint.pprint(Custom)
	print("avatar: ")
	pprint.pprint(avatar)
	
	token1 = event['sid']
	email = Custom['email']
	prompt = Custom['prompt']
	# gptPrompt = Custom['gptPrompt']
	time = Custom['time']
	InvestorLoginHistoryResponse = InvestorLoginHistory.get_item(Key={'email' :email,'time':time})
	InvestorLoginHistoryResponse = InvestorLoginHistoryResponse['Item']
	datanew = InvestorLoginHistoryResponse['data']
	userData=user.get_item(Key={'email' : email})
	userData=userData['Item']
	if avatar['type']=="WELCOME":
		# data1="Hi "+ Custom['name']+", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"
		print(f"prompt: {prompt}")
		if prompt:
			data1 = prompt
		else:
			data1 = "Hello. Please say hello to start. Hold down the spacebar when talking to me."
		link,imageUrl,textaddon,followup="","","",""
		# data1,link,imageUrl,textaddon,followup=linkandtextSepration(data1)
		dicinewlog={"user":"{Initialise}","bot":data1}
		# dicinewlog={"bot":data1}
		datanew.append(dicinewlog)
		InvestorLoginHistoryResponse['data'] =datanew
		InvestorLoginHistory.put_item(Item=InvestorLoginHistoryResponse)
		# if userData['firstTime']:
		#     userData['firstTime']=False
		#     user.put_item(Item=userData)
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
		print("user utterance: " + event['fm-question'])
		print(f"userData['StartTestSeries']: {userData['StartTestSeries']}")
		if len(event['fm-question'])==0:
			data1 = "I didn't hear anything, please try again."
		elif event['fm-question'].lower() in ["show verbal commands","show verbal command","show available commands","call verbal commands","show me verbal commands","show marble command","to verbal commands","show border commands","show barbie commands"]:
			data1 = "The verbal commands that you can use <ul><li>Open test series page.</li><li>Open the dashboard.</li><li>Open my profile.</li><li>Please hide.</li><li>Please show yourself.</li><li>Display full screen.</li><li>Minimize the screen.</li><li>Enable my subtitles.</li><li>Disable subtitles.</li><li>Show your subtitles.</li><li>Hide your subtitles.</li><li>Show question.</li><li>Hide question.</li><li>Please logout.</li></ul>"
		elif event['fm-question'].lower() =='fine':
			data1 ="Great." 
		elif event['fm-question'].lower() =='stop':
			if userData['StartTestSeries']==True:
				data1 ="Closing the quiz." 
				userData['StartTestSeries']=False
				user.put_item(Item = userData)
			else:
				# data1="Ok."
				data1 = "In the name, of love. Before, you, break, my heart."         
		elif event['fm-question'].lower() =='i am here':
			data1 ="Ok, Good." 
		# elif (event['fm-question'].lower() =='no:
		#     if userData['StartTestSeries']==True:
		#         data1 = "Ok. Take a break.<br>You can say 'Stop' to close the test."    
		#     else:
		#         data1="Ok."
		#         # data1 = "I didn't hear anything, please try again."  # TODO: this should change
		
		# replacing the above to workaround problem with utterance "no" never getting sent to Rasa
		elif (event['fm-question'].lower()=='no' and userData['StartTestSeries']==True):
			data1 = "Ok. Take a break.<br>You can say 'Stop' to close the test."    

		elif event['fm-question'].lower() in ['show options','show option','show answers','show answer','options','option']:
			if userData['StartTestSeries']==True:
				Token_Data_Response = Token_Data.get_item(Key={'token' : token1})
				if 'QuestionId' in Token_Data_Response['Item']:
					QID = Token_Data_Response['Item']['QuestionId']
					Record_Response = Record.get_item(Key={'userId' :email,'QuestionId':QID})
					Record_Response = Record_Response['Item']
					CurrentPostion=Record_Response['CurrentPostion']
					CurrentPostion1=int(CurrentPostion)+1
					Qdata = Record_Response['Question'][int(Record_Response['CurrentPostion'])]
					options = Qdata["options"]
					Question = Qdata["Question"]
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
					data1 =html
				else:
					data1 = "Can you please repeat the sentence."
			else:
				data1="Ok."
				# data1 = "Can you repeat the question." 
		
		elif event['fm-question'].lower() =='repeat':
			if userData['StartTestSeries']==True:
				Token_Data_Response = Token_Data.get_item(Key={'token' : token1})
				if 'QuestionId' in Token_Data_Response['Item']:
					QID = Token_Data_Response['Item']['QuestionId']
					Record_Response = Record.get_item(Key={'userId' :email,'QuestionId':QID})
					Record_Response = Record_Response['Item']
					CurrentPostion=Record_Response['CurrentPostion']
					CurrentPostion1=int(CurrentPostion)+1
					Qdata = Record_Response['Question'][int(Record_Response['CurrentPostion'])]
					options = Qdata["options"]
					Question = Qdata["Question"]
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
					data1 =AC1 + html
				else:
					data1 = "Can you please repeat the sentence."
			else:
				data1="Ok."
				# data1 = "Can you repeat the question." 
		elif (event['fm-question'].lower()=='yes' and userData['StartTestSeries']==True):
			# if userData['StartTestSeries']==True:
				Token_Data_Response = Token_Data.get_item(Key={'token' : token1})
				if 'QuestionId' in Token_Data_Response['Item']:
					QID = Token_Data_Response['Item']['QuestionId']
					Record_Response = Record.get_item(Key={'userId' :email,'QuestionId':QID})
					Record_Response = Record_Response['Item']
					CurrentPostion=Record_Response['CurrentPostion']
					if CurrentPostion <=Record_Response['Total Question'] -1:
						CurrentPostion1=int(CurrentPostion)+1
						Qdata = Record_Response['Question'][int(CurrentPostion)]
						options = Qdata["options"]
						Question = Qdata["Question"]
						AC1 ="Question "+str(CurrentPostion1)+". "+ Question 
						# html = "<ul>\n"
						html =""
						for option in options:
							html += f"{option}<br>\n"
						# html += "</ul>"
						data1 =AC1 + html
						
						dicinew = {
							"Question":AC1,
							"options":options,
							"Output":"",
							"Test":"",
							"text":data1
						}
					else:
						Record_Response['CurrentPostion'] = 0
						Record_Response['CurrentAnswerPostion']=0
						Record_Response['TestSeriesStatus'] = 0
						Qdata = Question_Data.get_item(Key={'id':QID})
						Record_Response["Total Question"]=len(Qdata['Item']['question'])
						Record_Response['Question']=Qdata['Item']['question']
						Record.put_item(Item = Record_Response)
						data1="The test is completed. Please say or write 'Stop' to exit."
				else:
					data1 = "Can you please repeat the sentence."
			# else:
			#     data1="Ok."
			#     # data1 = "Can you repeat the question." 
		else:
			Token_Data_Response = Token_Data.get_item(Key={'token' : token1})
			# if 'QuestionId' in Token_Data_Response['Item']:
			if False: #placeholder to bypass bug
				QID = Token_Data_Response['Item']['QuestionId']
				Record_Response = Record.get_item(Key={'userId' :email,'QuestionId':QID})
				Record_Response = Record_Response['Item']
			else:
				Record_Response={}
			if "Question" in Record_Response:
				if int(Record_Response['Total Question']) == int(Record_Response['CurrentPostion']):
					Value = False
				else:
					answerdata,Value= ResponseData(Record_Response['Question'][int(Record_Response['CurrentPostion'])]['options'],event["fm-question"])
			else:
				Value=False
			l=[]
			if Value==False:
				# print("preparing Rasa call")
				url="http://44.227.166.222:5002/webhooks/rest/webhook"  # eddie demo dev
				# url ="http://54.191.88.2:5005/webhooks/rest/webhook"   # Demo Investor?
				# url="http://52.11.66.129:5002/webhooks/rest/webhook"
				# url ="http://35.91.228.35:5002/webhooks/rest/webhook"
				# Todo: Don't need to send user name each time
				encoded_data = json.dumps({ "sender": "eddie", "message": event["fm-question"], "metadata": {"first-name": Custom['name']} })
				print("Rasa encoded_data: " )
				pprint.pprint(encoded_data)
				print("Calling Rasa")
				resp = http.request('POST',url,body=encoded_data,headers={'Content-Type': 'application/json'})
				data=json.loads(resp.data.decode('utf-8'))
				print("data post Rasa call: ")
				print(data)
				if len(data)==0:
					if userData["gpt3"]==True:
						print("calling ChatGPT with question: " + event["fm-question"])
						datafromopenAI=APICall(event["fm-question"],userData['gptPrompt'])
						print("datafromopenAI: ")
						print(datafromopenAI)
						if (('errorMessage' in datafromopenAI) or ('statusCode' in datafromopenAI)):
							data1 = "We got an error message back from ChatGPT "
							# random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
							# random_number_no_response  =random.randint(0,len(random_no_response)-1)
							# data1=random_no_response[random_number_no_response]
							print(f"OpenAI error messsage: {datafromopenAI}")
						else:
							data1=datafromopenAI
							test1 ="<br>Source: OpenAI" 
					else:
						random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
						random_number_no_response  =random.randint(0,len(random_no_response)-1)
						data1=random_no_response[random_number_no_response]
						
				for i in range(0,len(data)):
					data1=data[i]['text']
					
					if data1 in ['07481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','17481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','27481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','37481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=','47481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=']:
						if userData['StartTestSeries']==True:
							description=Record_Response['Question'][int(Record_Response['CurrentPostion'])]['description']
							data1=int(linkandtextSeprationText(data1))
							# question11=Record_Response['Question'][int(Record_Response['CurrentPostion'])]['Question']
							options = Record_Response['Question'][int(Record_Response['CurrentPostion'])]['options']
							dicinew={
								"options":options
							}
							correctPostioin =int(Record_Response['Question'][int(Record_Response['CurrentPostion'])]['correctPostioin'])
							if data1 == correctPostioin:
								Record_Response['CorrectAnswerbyYou']=Record_Response['CorrectAnswerbyYou']+1
								Record_Response['CurrentAnswerPostion']=Record_Response['CurrentAnswerPostion']+1
								Record_Response['CurrentPostion']=Record_Response['CurrentPostion']+1
								Record_Response['TestSeriesStatus'] ="Resume"
								gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
								random_number1  =random.randint(0,len(gesture)-1)
								l.append(gesture[random_number1]+description[data1])
								# l.append(description[data1])
								
								l.append("<br><br>Shall we move to the next question?")
								data1 = ' '.join(l)
								data3 = "Test"

								# data1 = l
								Record.put_item(Item = Record_Response)
							else:
								data1=description[data1]
								gesture  = ["Alas! ","Nice try but ","Too bad, ","Good attempt but "]
								random_number1  =random.randint(0,len(gesture)-1)
								l.append(gesture[random_number1]+data1)
								
								# l.append(data1)
								l.append("<br>The correct Answer is - ")
								correctAnswer = Record_Response['Question'][int(Record_Response['CurrentPostion'])]['correctAnswer']
								correctAnswer = correctAnswer[3:] 
								correctAnswer = correctAnswer.split('.')[0]
								l.append('"'+correctAnswer+'".')
								Record_Response['CurrentAnswerPostion']=Record_Response['CurrentAnswerPostion']+1
								Record_Response['CurrentPostion']=Record_Response['CurrentPostion']+1
								Record_Response['TestSeriesStatus'] ="Resume"
								Record.put_item(Item = Record_Response)
								l.append("<br><br>Shall we move to the next question?")
								data1 = ' '.join(l)
								data3 = "Test"
								# data1 = l
						else:
							data1="Ok."
							# data1 = "Can you repeat the question." 
					else:
						if data1 =='repeat7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
							if userData['StartTestSeries']==True:
								data1,dicinew =get_question_html(Record_Response)
							else:
								data1="Ok."
								# data1 = "Can you repeat the question." 
						elif data1 =='yes7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
							if userData['StartTestSeries']==True:
								data1,dicinew  = get_next_question_html(token1,email) 
							else:
								data1="Ok."
								# data1 = "Can you repeat the question."
						elif data1 =='stop7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=':
							if userData['StartTestSeries']==True:                      
								data1 ="Closing the quiz." 
								userData['StartTestSeries']=False
								user.put_item(Item = userData)
							else:
								data1 ="stop" 
						else:
							l.append(data1)
							# l.append('<br>')
							data1 = ' '.join(l) 
							# data1 = l

			else:
				correctPostioin =int(Record_Response['Question'][int(Record_Response['CurrentPostion'])]['correctPostioin'])
				description = Record_Response['Question'][int(Record_Response['CurrentPostion'])]['description']
				options = Record_Response['Question'][int(Record_Response['CurrentPostion'])]['options']
				dicinew={
					"options":options
				}
				
				if answerdata == correctPostioin:
					Record_Response['CorrectAnswerbyYou']=Record_Response['CorrectAnswerbyYou']+1
					Record_Response['CurrentAnswerPostion'] =Record_Response['CurrentAnswerPostion']+1
					Record_Response['CurrentPostion']=Record_Response['CurrentPostion']+1
					Record_Response['TestSeriesStatus'] ="Resume"
					gesture  = ["You are doing great, ","Very good, ","Outstanding, ","Excellent, "]
					random_number1  =random.randint(0,len(gesture)-1)
					l.append(gesture[random_number1]+description[answerdata])
					# l.append(description[answerdata])
					l.append("<br><br>Shall we move to the next question?")
					data1 = ' '.join(l)
					data3 = "Test"

					# data1 = l
					Record.put_item(Item = Record_Response)
				else:
					data1=description[answerdata]
					gesture  = ["Alas! ","Nice try but ","Too bad, ","Good attempt but "]
					random_number1  =random.randint(0,len(gesture)-1)
					l.append(gesture[random_number1]+data1)       
					# l.append(data1)
					l.append("<br>The correct Answer is - ")
					correctAnswer = Record_Response['Question'][int(Record_Response['CurrentPostion'])]['correctAnswer']
					correctAnswer = correctAnswer[3:]
					correctAnswer = correctAnswer.split('.')[0]
					l.append('"'+correctAnswer+'".')
					Record_Response['CurrentAnswerPostion'] =Record_Response['CurrentAnswerPostion']+1
					Record_Response['CurrentPostion']=Record_Response['CurrentPostion']+1
					Record_Response['TestSeriesStatus'] ="Resume"
					Record.put_item(Item = Record_Response)
					l.append("<br><br>Shall we move to the next question?")
					data1 = ' '.join(l)
					data3 = "Test"
		data1,link,imageUrl,textaddon,followup=linkandtextSepration(data1)
		dicinewlog={"user":event["fm-question"],"bot":data1}
		datanew.append(dicinewlog)
		InvestorLoginHistoryResponse['data'] =datanew
		InvestorLoginHistory.put_item(Item=InvestorLoginHistoryResponse)
	data2 = data1
	if test1 !="":
		if data1[0]=='"':
			data1=data1[1:]
			if data1[-1]=='"':
				data1=data1[:-1]
			else:
				pass
		else:
			pass
		data1 = str(data1 + test1)
		print("data1: "+ data1)
	data5=data2.replace('edYOU','e-dee-you')
	data4 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+data5+'</mstts:express-as></voice></speak>'
	# print("data4: " + data4)
	dicinew['description']=textaddon
	dicinew['link']=link
	dicinew['imageUrl']=imageUrl
	dicinew['followup']=followup
	if "options" in dicinew:
		if "Question" in dicinew:
			pass
		else:
			dicinew['Question']=""
			if data3 =="":
				dicinew['Output'] = data1
				dicinew['Test']=data3
				dicinew['text']=data2
			else:    
				dicinew['Output'] = ""
				dicinew['Test']=data1
				dicinew['text']=data2        
	else:
		dicinew['Question']=""
		# if type(data1) ==list:
			# data1 = ' '.join(data1)
		dicinew['options']=[]
		if data3 =="":
			dicinew['Output'] = data1
			dicinew['Test']=data3
			dicinew['text']=data2
		else:    
			dicinew['Output'] = ""
			dicinew['Test']=data1
			dicinew['text']=data2
		# else:
		#     dicinew['options']=[data1]
	instructions = {
		"customData": dicinew
	}
	
	dici = {'answer':data4,"instructions":instructions}
	print(f"dici : {dici}")
	# print(dici)
	# dici = {'answer':data1}
	print("returning from lambda_handler\n\n\n\n\n\n\n\n\n")
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

def get_question_html(Record_Response):
	Qdata = Record_Response['Question'][int(Record_Response['CurrentPostion'])]
	CurrentPostion = Record_Response['CurrentPostion']
	CurrentPostion1 = int(CurrentPostion)+1
	options = Qdata["options"]
	Question = Qdata["Question"]
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
	# data1 = dici
	# return AC + html
	# return data1
	return data,dicinew


def get_next_question_html(token1, email):
	Token_Data_Response = Token_Data.get_item(Key={'token': token1})
	if 'QuestionId' in Token_Data_Response['Item']:
		QID = Token_Data_Response['Item']['QuestionId']
		Record_Response = Record.get_item(Key={'userId': email, 'QuestionId': QID})
		Record_Response = Record_Response['Item']
		CurrentPostion = Record_Response['CurrentPostion']
		if CurrentPostion <= Record_Response['Total Question']-1:
			CurrentPostion1 = int(CurrentPostion)+1
			Qdata = Record_Response['Question'][int(Record_Response['CurrentPostion'])]
			options = Qdata["options"]
			Question = Qdata["Question"]
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
			Record_Response['CurrentPostion'] = 0
			Record_Response['CurrentAnswerPostion']= 0
			Record_Response['TestSeriesStatus'] = 0
			Record.put_item(Item=Record_Response)
			return "The test is complete. Please say or write 'Stop' to exit.",{}
	else:
		# uhm no, there will be other uses of saying the word yes, obviously
		# return "Please start the test first.",{}
		return


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