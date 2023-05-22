import json
import boto3
dynamodb = boto3.resource('dynamodb')
Topic = dynamodb.Table('Topic')
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
        # ,"industry",
        required_fields = ["Topic_id","token","topicName","description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            result=Topic.get_item(Key={'Topic_id': event['Topic_id']})
            if 'Item' in result:
                data=result['Item']
                data['topicName']=event['topicName']
                data['industry']=event['industry']
                data['description']=event['description']
                data['status']=event['status']
                Topic.put_item(Item=data) 
                # data['']
            
            # Topic.update_item(
            #     Key={
            #             'Topic_id': event['Topic_id'],
            #         },
            #         # industry=:industry,
            #     UpdateExpression="set topicName=:topicName, description=:description,status=:status",
            #     ExpressionAttributeValues={
            #             ':topicName':event['topicName'],
            #             ':industry':event['industry'],
            #             ':description':event['description'],
            #             ':status':event['status']
            #         },
            #     ReturnValues="UPDATED_NEW"
            #     )
            
            return {
                'statusCode': 200,
                'body': 'Topic updated successfully'
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
