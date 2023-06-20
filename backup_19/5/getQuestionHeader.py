import json
import boto3
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
    try:
        data =event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
        # TODO implement
            response = Question.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = Question.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            tenantlist=[]
            adminlist=[]
            if 'email' not in event:
                event['email']=""
                event['role']=""
            for i in result:
                if event['email']==i['Tenantemail']:
                    dici={}
                    dici['id']=i["id"]
                    dici["topic"]=i["topic"]
                    dici["description"]=i["description"]
                    # dici["max_marks"]=i["max_marks"]
                    # dici["no_of_question"]=i['no_of_question']
                    dici["series_title"]=i['series_title']
                    dici['Tenantemail']=i['Tenantemail']
                    dici['name']=i['name']
                    dici['status']=i['status']
                    dici['created_at']=i['created_at']
                    tenantlist.append(dici)
                if event['role']=="Admin":
                    dici={}
                    dici['id']=i["id"]
                    dici["topic"]=i["topic"]
                    dici["description"]=i["description"]
                    # dici["max_marks"]=i["max_marks"]
                    # dici["no_of_question"]=i['no_of_question']
                    dici["series_title"]=i['series_title']
                    dici['Tenantemail']=i['Tenantemail']
                    dici['name']=i['name']
                    dici['status']=i['status']
                    dici['created_at']=i['created_at']
                    adminlist.append(dici)
            
            if event['role']=="Admin":
                if len(adminlist)>0:
                    adminlist.sort(key = lambda x:x['created_at'],reverse =False)
                    return {
                        'statusCode': 200,
                        'body': adminlist
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No test series are added yet"
                    }
            else:
                if len(tenantlist)>0:
                    tenantlist.sort(key = lambda x:x['created_at'],reverse =False)
                    return {
                        'statusCode': 200,
                        'body': tenantlist
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No test series are added yet"
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
    