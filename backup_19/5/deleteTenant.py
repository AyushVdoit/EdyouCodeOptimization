import json
import boto3
default_region = "us-west-2"
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Topic=dynamodb.Table('Topic')
Investor = dynamodb.Table('Investor')
Token_Data = dynamodb.Table('Token')
Question = dynamodb.Table('Question')
clientEc2 = boto3.client('ec2', region_name=default_region)

def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    try:
        data =event
        required_fields = ["token","email","status"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
                }
        if TokenChecker(event['token']):
            print(event)
            email = event['email'].lower()

            if event['status']=='Delete':
                print("-------------------------------")
                resp=user.get_item(Key={'email' : email})
                if 'Item'in resp:
                    instance_id =resp['Item']['instance_id']
                # print(instance_id)
                print("In Topic")
                response = Topic.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = Topic.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])
                for i in result:
                    if event['email']==i['Tenantemail']:
                        if i['status']=="Active":
                            i['status']="Delete"
                            Topic.put_item(Item=i)
                print("In Test Series")
                response = Question.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = Question.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])
                for i in result:
                    if event['email']==i['Tenantemail']:
                        if i['status']=="Active":
                            i['status']="Delete"
                            Question.put_item(Item=i)
                
                print("In user")
                response = user.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = user.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])
                l=[]
                dici={}
                for i in result:
                    if i['role'] =="User":
                        l.append(i)
                for i in l:
                    if event['email']==i['tenantEmail']:
                        response = user.delete_item(
                            Key={
                                'email': i['email'],
                                },
                            )
                        # print(i['email'])
                print("investor")
                response = Investor.delete_item(
                Key={
                    'email': email,
                    },
                )
                
                print("Tenant")
                    
                response = user.delete_item(
                Key={
                    'email': email,
                    },
                )
                clientEc2.terminate_instances(InstanceIds=[instance_id])
                return {
                    'statusCode': 200,
                    'body': f'Tenant deleted successfully'
                }
            else:
                return {
                    'statusCode': 401,
                    'body': 'done'
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
    
