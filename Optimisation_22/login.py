import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key
from werkzeug.security import check_password_hash
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
import string
import random
import smtplib

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get user and token tables
user_table = dynamodb.Table('user')
token_table = dynamodb.Table('Token')

def lambda_handler(event, context):
    print(event)
    res = check_email(event['email'])
    
    if res['found']:
        data = res['data']
        role = res['role']
        
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        data['last_login'] = now
        
        created_date = strftime("%Y-%m-%d", gmtime())
        begin_date = datetime.strptime(created_date, "%Y-%m-%d")
        end_date = begin_date + timedelta(days=10)
        end_date = str(end_date).split(" ")[0]
        
        if role == 'admin':
            if check_password_hash(data['password'], event['password']):
                if event['device'] == 'mobile':
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    token_table.put_item(Item=token_data)
                    user_table.put_item(Item=data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                else:
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    token_table.put_item(Item=token_data)
                    user_table.put_item(Item=data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
            else:
                return {'statusCode': 401, 'body': 'Password is incorrect'}
        
        elif role == 'Tenant':
            if check_password_hash(data['password'], event['password']):
                if event['device'] == 'mobile':
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    token_table.put_item(Item=token_data)
                    user_table.put_item(Item=data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                else:
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    token_table.put_item(Item=token_data)
                    user_table.put_item(Item=data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
            else:
                return {'statusCode': 401, 'body': 'Password is incorrect'}
        
        elif role == 'executiveAdmin':
            if check_password_hash(data['password'], event['password']):
                if event['device'] == 'mobile':
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    user_table.put_item(Item=data)
                    token_table.put_item(Item=token_data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                else:
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    user_table.put_item(Item=data)
                    token_table.put_item(Item=token_data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
            else:
                return {'statusCode': 401, 'body': 'Password is incorrect'}
        
        elif role == 'user':
            status = res['status']
            
            if status == "Pending":
                return {'statusCode': 401, 'body': 'Your signup request is pending with admin!'}
            
            if status == "Inactive":
                return {'statusCode': 401, 'body': 'Your account is inactive'}
            
            else:
                if check_password_hash(data['password'], event['password']):
                    if event['device'] == 'mobile':
                        token = secrets.token_urlsafe(20)
                        user_id = data['id']
                        token_data = {
                            'token': token,
                            'created_at': created_date,
                            'expired_at': end_date,
                            'id': user_id
                        }
                        user_table.put_item(Item=data)
                        token_table.put_item(Item=token_data)
                        return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                    else:
                        token = secrets.token_urlsafe(20)
                        user_id = data['id']
                        token_data = {
                            'token': token,
                            'created_at': created_date,
                            'expired_at': end_date,
                            'id': user_id
                        }
                        user_table.put_item(Item=data)
                        token_table.put_item(Item=token_data)
                        return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                else:
                    return {'statusCode': 401, 'body': 'Password is incorrect'}
        
        elif role == 'AvatarRecorder':
            if check_password_hash(data['password'], event['password']):
                if event['device'] == 'mobile':
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    user_table.put_item(Item=data)
                    token_table.put_item(Item=token_data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
                else:
                    token = secrets.token_urlsafe(20)
                    user_id = data['id']
                    token_data = {
                        'token': token,
                        'created_at': created_date,
                        'expired_at': end_date,
                        'id': user_id
                    }
                    user_table.put_item(Item=data)
                    token_table.put_item(Item=token_data)
                    return {'statusCode': 200, 'body': 'Logged in', 'data': data, 'Token': token}
            else:
                return {'statusCode': 401, 'body': 'Password is incorrect'}
        
        else:
            return{
                'body':'No email found',
                'statusCode':402
            } 
    
    else:
        return{
            'body':'No email found',
            'statusCode':402
        }


def check_email(email):
    email=email.lower()	
    data2 =user.get_item(Key={'email':email})	
    if 'Item' in data2:	
        if data2['Item']['role']=='Admin':	
            data={	
                'found':True,	
                'data':data2['Item'],	
                'role':'admin'    	
            }	
        elif data2['Item']['role']=='executiveAdmin':	
            data={	
                'found':True,	
                'data':data2['Item'],	
                'role':'executiveAdmin'    	
            }	
        elif data2['Item']['role']=='AvatarRecorder':	
            data={	
                'found':True,	
                'data':data2['Item'],	
                'role':'AvatarRecorder'    	
            }	
        	
        elif data2['Item']['role']=='Tenant':	
            data={	
                'found':True,	
                'data':data2['Item'],	
                'role':'Tenant'	
            }	
        else:	
            data={	
                'found':True,	
                'data':data2['Item'],	
                'role':'user',	
                'status':data2['Item']['status']	
            }	
    else:	
        data={	
            'found':False	
        }	
    return data
