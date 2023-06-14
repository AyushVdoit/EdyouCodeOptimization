import json
import boto3
dynamodb = boto3.resource('dynamodb')
Presentation=dynamodb.Table('Presentation')
user = dynamodb.Table("Investor")
Token_Data = dynamodb.Table('Token')
def token_checker(email,token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        Data = user.get_item(Key={'email': email})
        if 'Item' in Data:
            if Data['Item']['token']==token:
                return True
            else:
                return False
        else:
            return False
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
        if token_checker(event['email'].lower(),event['token']):
            # TODO implement
            response = Presentation.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = Presentation.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            tenantlist=[]
            adminlist=[]
            # count=0
            if event['Tenantemail'] =="":
                for i in result:
                    if i['Tenantemail']=="":
                        if i['status']=="Active":
                            if i['URL']!="":
                                adminlist.append(i) 
            else:
                for i in result:
                # print(f"{count} {i['Tenantemail']}")
                    if event['Tenantemail']==i['Tenantemail']:
                        if i['status']=="Active":
                            if i['URL']!="":
                                tenantlist.append(i)
                    elif i['Tenantemail']!="":
                        pass
                    # else:
                    #     if i['status']=="Active":
                    #         adminlist.append(i)
                    # # count=count+1
            if event['Tenantemail']=="":
                return {
                        "list":"Admin",
                        'statusCode': 200,
                        'body': adminlist
                    }
            elif event['Tenantemail']!="":
                return {
                        "list":"Tenant",
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
                'body': 'You have logged in from another device, please close from that device and re-login to continue.'
            }
        
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
    