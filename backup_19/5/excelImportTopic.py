import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
Topic=dynamodb.Table('Topic')
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
            required_fields = ["Answer","QuestionVariation_1","QuestionVariation_2","QuestionVariation_3"]
            OptionsGiven={"Answer":"A","QuestionVariation_1":"B","QuestionVariation_2":"C","QuestionVariation_3":"D"}
            for field in required_fields:
                if field not in d or not d[field]:
                    l.append(OptionsGiven[field]+str(count))
        if len(l)>0:
            string = ', '.join(l)
            return {
                'statusCode': 400,
                'body': textnew + string
            }
        data2 =Topic.get_item(Key={'Topic_id':event['Topic_id']})
        
        if 'Item' in data2:
            TopicDicitionary=data2['Item']
            # print(TopicDicitionary)
            question1=TopicDicitionary['question']
            for k in data:
                descriptions = []
                for key in k:
                    if key.startswith("QuestionVariation_"):
                        if k[key]!="":
                            descriptions.append({"subQ":k[key]})
                
                question={}
                question['Potential_Question']=descriptions
                question['correctAnswer']=k['Answer']+"7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup="
                question['qid']=uuid4().hex
                question['followup_status']=False
                question['prompt_status']=False
                question['followup']=""
                question['image']=""
                question['imageUrl']=""
                question['url']=""
                question1.append(question)
                TopicDicitionary['question'] = question1
            Topic.put_item(Item=TopicDicitionary)        
    
    return {
        'statusCode': 200,
        'body':"File Uploaded Succesfully"
    }
