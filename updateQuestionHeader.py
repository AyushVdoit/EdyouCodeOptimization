import json
import boto3

dynamodb = boto3.resource('dynamodb')
Question = dynamodb.Table('Question')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
    data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in data:
        return True
    else:
        return False  
    
# to update question header
def lambda_handler(event, context):
    try:
        data = event
        required_fields = ["id","topic","description","max_marks","series_title","no_of_question"]
        # check if required fields are present
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            # if event['email'] in ['admin@edyou.com','admin@edyou.in']:
            #     if event['tenantEmail']=="":
            #         event['email']=""
            #     else:
            #         event['email']=event['tenantEmail']
            question_info = Question.get_item(Key={'id': event['id']})
            if 'Item' in question_info:
                data=question_info['Item']
                # if event['email']=="":
                data['topic']= event['topic']
                data['description']=event['description']
                data['max_marks']=event['max_marks']
                data['series_title']=event['series_title']
                data['no_of_question']=event['no_of_question']
            # else:
                    # data['topic']= event['topic']
                    # data['description']=event['description']
                    # data['max_marks']=event['max_marks']
                    # data['series_title']=event['series_title']
                    # data['no_of_question']=event['no_of_question']
                Question.put_item(Item=data) 
            # Question.update_item(
            #     Key={
            #             'id': event['id'],
            #         },
            #     UpdateExpression="set description = :description,no_of_question=:no_of_question, max_marks=:max_marks, series_title=:series_title, topic=:topic,Tenantemail=:Tenantemail",
            #     ExpressionAttributeValues={
            #             ':topic': event['topic'],
            #             ':description':event['description'],
            #             ':max_marks':event['max_marks'],
            #             ':series_title':event['series_title'],
            #             ':no_of_question':event['no_of_question'],
            #             ':Tenantemail':event['email']
            #         },
            #     ReturnValues="UPDATED_NEW"
            #     )
            
            return {
                'statusCode': 200,
                'body': 'Updated Successfully'
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
