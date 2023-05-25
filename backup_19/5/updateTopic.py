import json
import boto3
from uuid import uuid4
import base64
s3 = boto3.client('s3')
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
    try:
        data =event
        required_fields = ["Topic_id","token","qid","correctAnswer","Potential_Question"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            
            data2 =Topic.get_item(Key={'Topic_id':event["Topic_id"]})
            if 'Item' in data2:
                topicDictionary=data2['Item']
                topic1=topicDictionary['question']
                topic={}
                for question in event["Potential_Question"]:
                    if question['subQ'] is None or question['subQ'].strip() == '':
                        return {
                            'statusCode': 400,
                            'body': 'Question variations are required and cannot be empty'
                            }
                bucket_name="pollydemo2022"
                object_key='images_dev/'+event['qid']+'.jpg'
                if event['imageUrl'] !="":
                    content_type = 'image/jpeg'
                    if "https://pollydemo2022.s3.us-west-2.amazonaws.com/" in event['imageUrl']:
                        event['image']= event['imageUrl']
                    else:
                        image=event['imageUrl'].replace("data:image/png;base64,","")
                        image = base64.b64decode(image)
                        s3.put_object(Bucket=bucket_name, Key=object_key, Body=image, ContentType=content_type)
                        event['image']="https://pollydemo2022.s3.us-west-2.amazonaws.com/"+object_key
                    topic['image']=event['image']
                    topic['imageUrl']=event['image']
                else:
                    topic['image']=""
                    topic['imageUrl']=""
                if event['url']!=""  and event['url']!=None :
                    topic['url']=event['url']
                else:
                    topic['url']=""
                    
                if event['description']!=""  and event['description']!=None:
                    if event['prompt_status']==True or event['prompt_status']!=None:
                        topic['description']= event['description']
                    else:
                        topic['description']=""
                        event['prompt_status']=False
                else:
                    topic['description']=""
                if event['url']!="" and event['url']!=None:
                    topic['url']=event['url']
                    if event['followup']!=""  and event['followup']!=None :
                        if event['followup_status']:
                            topic['followup']= event['followup']
                        else:
                            topic['followup']="click me"
                    else:
                        topic['followup']="click me"
                    # else
                    # topic['followup']= event['followup']
                else:
                    topic['url']=""
                    topic['followup']= ""
        
                topic['correctAnswer']=event['correctAnswer']+"7481903939urlforyou="+topic['url']+"7581903939imagelinkforyou="+topic['image']+"7581904949Textlinkforyou="+topic['description']+"7581904949Followup="+topic['followup']
                # topic['correctAnswer']=event['correctAnswer']+"7481903939urlforyou="+topic['url']+"7581903939imagelinkforyou="+topic['image']+"7581904949Textlinkforyou="+topic['description']
                topic["Potential_Question"]=event['Potential_Question']
                topic['qid']=event['qid']
                topic['prompt_status']=event['prompt_status']
                topic['followup_status']=event['followup_status']
                index = next((i for i, q in enumerate(topic1) if q['qid'] == event['qid']), None)
                if index is not None:
                    topic1[index] = topic
                    topicDictionary['question'] = topic1
                    Topic.put_item(Item=topicDictionary)
                    return {
                        'statusCode': 200,
                        'body': "Question updated successfully"
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