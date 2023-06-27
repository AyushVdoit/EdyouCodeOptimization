import json
import boto3
from time import gmtime, strftime
from uuid import uuid4
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
    required_fields = ["id","token","qid","correctAnswer","description","options","Question"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
            'statusCode': 400,
            'body': f'Error: {field} is required and cannot be empty'
            }
    if TokenChecker(event['token']):
        data2 =Question.get_item(Key={'id':event["id"]})
        if 'Item' in data2:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            questionDictionary=data2['Item']
            question1=questionDictionary['question']
            question={}
            question['qid']=event['qid']    
            # letters = ["A.", "B.", "C.", "D.", "E."]
            # NewValue  = {"Option A":0,"Option B":1,"Option C":2,"Option D":3,"Option E":4}
            options=event['options']
            # options = [item for item in options if item is not None]
            options = [item for item in options if item is not None and item != ""]
            length1=len(options)
            letters = [chr(i+65)+"." for i in range(length1)]
            NewValue = {f"Option {chr(i+65)}":i for i in range(length1)}
            replacements = {i: chr(i+65) for i in range(length1)}
            
            new_options = []
            for i, option in enumerate(options):
                new_option = f"{letters[i]} {option}"
                new_options.append(new_option)
            position = NewValue[event['correctAnswer']]
            # replacements  = {0:"A",1: "B",2:"C",3:"D",4:"E"}
            question['correctAnswer']=letters[position]+" "+options[position]
            question['correctPostioin'] = position
            question['correctAnswerFrontend'] = event['correctAnswer']
            question["options"]=new_options
            description = event['description']
            # description = [item for item in description if item is not None]
            description = [item for item in description if item is not None and item != ""]

            if 'hint' in event:
                question['hint'] = event['hint']
            else:
                question['hint'] = ""
            for i, desc in enumerate(description):
                if description[i]==None:
                    continue
                if i == position:
                    description[i] = replacements[i]+" is correct because "+description[i]
                else:
                    description[i] = replacements[i]+" is incorrect because "+description[i]

            question['description']=description
            
            question["Question"]=event['Question']
            question['updated_at']=now
            question['updated_by']=event['creator_name']
            # question['created_at']=event['created_at']
            # question['created_by']=event['created_by']
            # question['created_at']=question1['created_at']
            # question['created_by']=question1['created_by']
            question['created_at']=now
            question['created_by']=""
            
            
            
            index = next((i for i, q in enumerate(question1) if q['qid'] == event['qid']), None)
            if index is not None:
                question1[index] = question
                questionDictionary['question'] = question1
                Question.put_item(Item=questionDictionary)
                return {
                    'statusCode': 200,
                    'body': "Question updated succesfully"
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
        
    # except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
    #     return {
    #         'statusCode': 400,
    #         'body': f'Error: {e}'
    #     }
