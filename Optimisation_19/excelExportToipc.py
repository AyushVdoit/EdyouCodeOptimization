import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
topic_table = dynamodb.Table('Topic')
token_table = dynamodb.Table('Token')

def token_checker(token):
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    if token_checker(event['token']):
        data = event['data']
        text_new = "The fields are missing at column "
        missing_fields = []
        row_count = 1
        for row in data:
            row_count += 1
            required_fields = ["Answer", "QuestionVariation_1", "QuestionVariation_2", "QuestionVariation_3"]
            options_given = {"Answer": "A", "QuestionVariation_1": "B", "QuestionVariation_2": "C", "QuestionVariation_3": "D"}
            for field in required_fields:
                if field not in row or not row[field]:
                    missing_fields.append(options_given[field] + str(row_count))
        
        if len(missing_fields) > 0:
            missing_fields_str = ', '.join(missing_fields)
            return {
                'statusCode': 400,
                'body': text_new + missing_fields_str
            }
        
        topic_data = topic_table.get_item(Key={'Topic_id': event['Topic_id']})
        
        if 'Item' in topic_data:
            topic_dictionary = topic_data['Item']
            question_list = topic_dictionary['question']
            
            for row in data:
                descriptions = []
                for key in row:
                    if key.startswith("QuestionVariation_"):
                        if row[key] != "":
                            descriptions.append({"subQ": row[key]})
                
                question = {
                    'Potential_Question': descriptions,
                    'correctAnswer': row['Answer'] + "7481903939urlforyou=7581903939imagelinkforyou=7581904949Textlinkforyou=7581904949Followup=",
                    'qid': uuid4().hex,
                    'followup_status': False,
                    'prompt_status': False,
                    'followup': "",
                    'image': "",
                    'imageUrl': "",
                    'url': ""
                }
                
                question_list.append(question)
                topic_dictionary['question'] = question_list
            
            topic_table.put_item(Item=topic_dictionary)
    
    return {
        'statusCode': 200,
        'body': "Import done"
    }
