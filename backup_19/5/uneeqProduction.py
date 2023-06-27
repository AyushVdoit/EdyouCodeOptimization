import json
import random
import requests
import boto3
from decimal import Decimal
import urllib3
http = urllib3.PoolManager()
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Question_Data = dynamodb.Table('Question_Prod')
Token_Data = dynamodb.Table('Token_Prod')
Record = dynamodb.Table("Record_Prod")
user = dynamodb.Table("user_Prod")
from difflib import SequenceMatcher
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
    print(event)
    avatar=event['fm-avatar']
    avatar=json.loads(avatar)
    Custom = event['fm-custom-data']
    Custom=json.loads(Custom)
    token1 = event['sid']
    email = Custom['email'] 
    dicinew={}
    if avatar['type']=="WELCOME":
        data1="Hi "+ Custom['name']+", welcome to the world of e-dee-YOU. I am Hannah. How can I help you?"
    else:
        userData=user.get_item(Key={'email' : email})
        userData=userData['Item']
        print(userData)
        if len(event['fm-question'])==0:
            data1 = "I didn't hear anything, please try again." 
        elif event['fm-question'].lower() in ['open test series','test','open series','test series','series','opening the test series','opening test series','go to test series']:
            data1 ='Sure, opening the test series.'
        elif event['fm-question'].lower() =='fine':
            data1 ="Great." 
        elif event['fm-question'].lower() =='stop':
            if userData['StartTestSeries']==True:
                data1 ="Closing the quiz." 
                userData['StartTestSeries']=False
                user.put_item(Item = userData)
            else:
                data1 = "I didn't hear anything, please try again." 
        
        elif event['fm-question'].lower() =='i am here':
            data1 ="Ok, Good." 
        elif event['fm-question'].lower() in ['open info box','box','open information box','information box']:
            data1 ='ok, opening info box'
            
        elif event['fm-question'].lower() in ['hide','hide yourself']:
            data1 ='hiding myself'
        
        elif event['fm-question'].lower() in ['unhide yourself','please show yourself','show yourself','I am not able to see you']:
            data1 ='Here I am'
        elif event['fm-question'].lower() =='no':
            if userData['StartTestSeries']==True:
                data1 = "Ok. Take a break.<br>You can say 'Stop' to close the test."    
            else:
                data1 = "I didn't hear anything, please try again." 
        
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
                        "Output":""
                    }
                    data1 =AC1 + html
                else:
                    data1 = "Can you please repeat the sentence."
            else:
                data1 = "Can you repeat the question." 
        elif event['fm-question'].lower() =='yes':
            if userData['StartTestSeries']==True:
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
                            "Output":""
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
            else:
                data1 = "Can you repeat the question." 
        else:
            Token_Data_Response = Token_Data.get_item(Key={'token' : token1})
            if 'QuestionId' in Token_Data_Response['Item']:
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
            if Value ==False:
                # url="http://52.11.66.129:5002/webhooks/rest/webhook"
                url = "http://52.32.57.141:5002/webhooks/rest/webhook"
                encoded_data = json.dumps({  "sender": "adarsh","message": event["fm-question"]})
                resp = http.request('POST',url,body=encoded_data,headers={'Content-Type': 'application/json'})
                data=json.loads(resp.data.decode('utf-8'))
                print(data)
                if len(data)==0:
                    random_no_response=["Sorry, I don't understand. Can you please repeat?","Sorry, I'm a bit confused. Can you please say it again?","I'm not sure I follow, could you clarify?","Pardon me, can you repeat the question?","Excuse me, I missed the point, can you please rephrase it?","My apologies, can you say that again in a different way?"]
                    random_number_no_response  =random.randint(0,len(random_no_response)-1)
                    data1=random_no_response[random_number_no_response]
                for i in range(0,len(data)):
                    data1=data[i]['text']
                    
                    if data1 in ['0','1','2','3','4']:
                        if userData['StartTestSeries']==True:
                            description=Record_Response['Question'][int(Record_Response['CurrentPostion'])]['description']
                            data1=int(data1)
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
                                # data1 = l
                        else:
                            data1 = "Can you repeat the question." 
                    else:
                        if data1 =='repeat':
                            if userData['StartTestSeries']==True:
                                data1,dicinew =get_question_html(Record_Response)
                            else:
                                data1 = "Can you repeat the question." 
                        elif data1 =='yes':
                            if userData['StartTestSeries']==True:
                                data1,dicinew  = get_next_question_html(token1,email) 
                            else:
                                data1 = "Can you repeat the question."
                        elif data1 =='stop':
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
                    # data1 = l
    # data1 =json.dumps(data1)
    # data1 = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-SaraNeural"><mstts:express-as style="friendly" styledegree="1.2">'+data1+'</mstts:express-as></voice></speak>'    
    data2 = data1.replace("<br>","")
    if "Question" in dicinew:
        pass
    else:
        dicinew['Question']=""
        # if type(data1) ==list:
            # data1 = ' '.join(data1)
        dicinew['options']=[]
        dicinew['Output'] = data1
        # else:
        #     dicinew['options']=[data1]
    instructions = {
        "customData": dicinew
    }
    
    # dici={'answer':data1,"instructions":json.dumps(instructions, separators=(',', ':'), ensure_ascii=False)}  
    dici = {'answer':data2,"instructions":instructions}
    print(dici)
    # dici = {'answer':data1}
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
        "Output":""
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
                "Output":""
            }
            return data,dicinew
        else:
            Record_Response['CurrentPostion'] = 0
            Record_Response['CurrentAnswerPostion']= 0
            Record_Response['TestSeriesStatus'] = 0
            Record.put_item(Item=Record_Response)
            return "The test is complete. Please say or write 'Stop' to exit.",{}
    else:
        return "Please start the test first.",{}
