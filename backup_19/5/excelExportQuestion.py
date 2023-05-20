import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Question=dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    if TokenChecker(event['token']):
        data = event['data']
        data1 = data
        textnew="The fields are missing at column "
        l=[]
        count=1
        for d in data1: 
            count+=1
            required_fields = ["correctAnswer","description__001","description__002","description__003","description__004","description__005","options__001","options__002","options__003","options__004","options__005","Question","hint"]
            OptionsGiven={'correctAnswer': 'A','description__001': 'B','description__002': 'C','description__003': 'D','description__004': 'E','description__005': 'F','options__001': 'G','options__002': 'H','options__003': 'I','options__004': 'J','options__005': 'K','Question': 'L','hint': 'M'}
            for field in required_fields:
                if field not in d or not d[field]:
                    l.append(OptionsGiven[field]+str(count))
                    
        if len(l)>0:
            
            string = ', '.join(l)
            return {
                'statusCode': 400,
                'body': textnew + string
            }
        
        data2 =Question.get_item(Key={'id':event['id']})
        
        if 'Item' in data2:
            questionDicitionary=data2['Item']
            question1=questionDicitionary['question']
            for k in data:
                descriptions = []
                options = []
                for key in k:
                    if key.startswith("description__"):
                        descriptions.append(k[key])
                    elif key.startswith("options__"):
                        options.append(k[key])
                question={}
                letters = ["A.", "B.", "C.", "D.", "E."]
                new_options = []
                for i, option in enumerate(options):
                    new_option = f"{letters[i]} {option}"
                    new_options.append(new_option)
                lowercase_strings = [s.lower() for s in options]
                position = lowercase_strings.index(k['correctAnswer'].lower())
                replacements  = {0:"A",1: "B",2:"C",3:"D",4:"E"}
                NewValue  = {0:"Option A",1:"Option B",2:"Option C",3:"Option D",4:"Option E"}
                question['correctAnswer']=letters[position]+" "+options[position]
                question['correctPostioin'] = position
                question["options"]=new_options
                if 'hint' in k:
                    question['hint'] = k['hint']
                else:
                    question['hint'] = ""
                for i, desc in enumerate(descriptions):
                    if i == position:
                        descriptions[i] = replacements[i]+" is correct because "+descriptions[i]
                    else:
                        descriptions[i] = replacements[i]+" is incorrect because "+descriptions[i]
    
                question['description']=descriptions
                question['correctAnswerFrontend'] = NewValue[position]

                question["Question"]=k['Question']
                question['qid']=uuid4().hex
                question1.append(question)
                questionDicitionary['question'] = question1
            Question.put_item(Item=questionDicitionary)        
            return {
                    'statusCode': 200,
                    'body': "File Uploaded Succesfully"
                }
    
