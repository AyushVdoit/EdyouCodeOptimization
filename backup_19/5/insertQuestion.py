import json
import boto3
from uuid import uuid4
import secrets
from time import gmtime, strftime

from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
import string
import random
import smtplib

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
    # try:
    data =event
    required_fields = ["id","token","Question","correctAnswer","description","options"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
            'statusCode': 400,
            'body': f'Error: {field} is required and cannot be empty'
            }
    if TokenChecker(event['token']):
        data2 =Question.get_item(Key={'id':event['id']})
        if 'Item' in data2:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            questionDicitionary=data2['Item']
            question1=questionDicitionary['question']
            question={}
            options=event['options']
            # options = [item for item in options if item is not None]
            options = [item for item in options if item is not None and item != ""]

            length1=len(options)
            letters = [chr(i+65)+"." for i in range(length1)]
            NewValue = {f"Option {chr(i+65)}":i for i in range(length1)}
            replacements = {i: chr(i+65) for i in range(length1)}
            # letters = ["A.", "B.", "C.", "D.", "E."]
            # NewValue  = {"Option A":0,"Option B":1,"Option C":2,"Option D":3,"Option E":4}
            # replacements  = {0:"A",1: "B",2:"C",3:"D",4:"E"}
            new_options = []
            for i, option in enumerate(options):
                new_option = f"{letters[i]} {option}"
                new_options.append(new_option)
            position = NewValue[event['correctAnswer']]
            question['correctAnswer']=letters[position]+" "+options[position]
            question['correctPostioin'] = position
            question['correctAnswerFrontend'] = event['correctAnswer']
            question["options"]=new_options
            if 'hint' in event:
                question['hint'] = event['hint']
            else:
                question['hint'] = ""
            description = event['description']
            # description = [item for item in description if item is not None]
            description = [item for item in description if item is not None and item != ""]

            
            print(options)
            print(description)
            for i, desc in enumerate(description):
                print(i)
                print(desc)
                if i == position:
                    description[i] = replacements[i]+" is correct because "+description[i]
                else:
                    description[i] = replacements[i]+" is incorrect because "+description[i]

            question['description']=description
            
            question["Question"]=event['Question']
            question['qid']=uuid4().hex
            question['hint'] = event['hint']
            question['created_at']=now
            question['updated_at']=now
            question['created_by']=event['creator_name']
            question['updated_by']=event['creator_name']
        
            question1.append(question)
            questionDicitionary['question'] = question1
            Question.put_item(Item=questionDicitionary)        
            return {
                'statusCode': 200,
                'body': "Question added successfully"
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
    # except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
    #     return {
    #         'statusCode': 400,
    #         'body': f'Error: {e}'
    #     }