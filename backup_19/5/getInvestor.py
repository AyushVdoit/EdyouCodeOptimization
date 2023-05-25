import json
import boto3
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')
Token_Data = dynamodb.Table('Token')
Token_Data_Prod = dynamodb.Table('Token_Prod')

def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        Data=Token_Data_Prod.get_item(Key={'token' : token})
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
            response = Investor.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = Investor.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            tenantlist=[]
            adminlist=[]
            if 'email' not in event:
                event['email']=""
                event['role']=""
            for i in result:
                if event['email']==i['tenantEmail']:
                    tenantlist.append(i)
                if event['role']=="Admin":
                    adminlist.append(i)
            if event['role']=="Admin":
                if len(adminlist)>0:
                    adminlist.sort(key = lambda x:x['created_at'])
                    return {
                        'statusCode': 200,
                        'body': adminlist
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No Investor added yet"
                    }
            else:
                if len(tenantlist)>0:
                    tenantlist.sort(key = lambda x:x['created_at'])
                    return {
                        'statusCode': 200,
                        'body': tenantlist
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No Inveestor added yet"
                    }
                        
            
            # l=[]
            # dici={}
            # for i in result:
            #     # if i['role'] =="Investor":
            #         l.append(i)
            # if len(result)>0:
            #     return {
            #         'statusCode': 200,
            #         'body': result
            #     }
            # else:
            #     return {
            #             'statusCode': 205,
            #             'body': "No investor are added yet"
            #         }
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
    
