import json
import boto3
from uuid import uuid4
import secrets
from time import gmtime, strftime
from boto3.dynamodb.conditions import Key
from werkzeug.security import  check_password_hash
import random
from datetime import datetime
import smtplib
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('Investor')
InvestorLoginHistory = dynamodb.Table('InvestorLoginHistory')
Token_Data = dynamodb.Table('Token')
def lambda_handler(event, context):
    res=checkemail(event['email'])
    if(res['found']):
        print("yes")
        data=res['data']
        role=res['role']
        if data['expiredPassword']==False:
            print("yes")
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            time_1 = datetime.strptime(now,"%Y-%m-%d,%H:%M:%S")
            time_2 = datetime.strptime(data['expired_at'],"%Y-%m-%d,%H:%M:%S")

            time_interval = time_2 - time_1
            # print(type(time_interval))
            time_interval=int(time_interval.total_seconds()* 1000000)
            if time_interval>0:
                print("yes")
                if data['password'] ==event['password']:
                    now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
                    token = secrets.token_urlsafe(20)
                    data['token'] = token
                    data['lastlogin']=now
                    data['firstTime']=True
                    data['Presentation_url']=""
                    data['Presentation']=False
                    data['Presentation_id']=""
                    data['Presentation_first_index']=0
                    data['Presentation_Current_index']=0
                    data['Presentation_last_index']=""
                    data['StartTestSeries']=False
                    data['LoginCheck']=True
                    user.put_item(Item=data)
                    Ipaddress=""
                    if 'Ipaddress' in event:
                        Ipaddress=event['Ipaddress']
                    dici={
                        'email':event['email'].lower(),
                        'time':now,
                        'data':[],
                        "logout":"",
                        "Session":"",
                        "Ip_Address":Ipaddress
                    }
                    
                    InvestorLoginHistory.put_item(Item=dici)
                    
                    data1={
                                'token':token,
                                'created_at':"",
                                'expired_at':""
                            }
                    Token_Data.put_item(Item=data1)
                    if data['instance_pvt_ip']=="172.31.56.87":
                        data['flag']= False
                        return {'statusCode': 200,'body': 'Logged in','data': data,'Token':token,'flag':False}
                    else:
                        data['flag']=True
                        return {'statusCode': 200,'body': 'Logged in','data': data,'Token':token,'flag':True}
    
                else:
                    return {'statusCode': 401,'body':'Password is incorrect'}
            else:
                data['expiredPassword'] = True
                data['expire_time']=0
                user.put_item(Item = data)
                return{
                    'body':'The link has expired. Please contact edYOU.',
                    'statusCode':402
                }
        else:
            return{
                    'body':'The link has expired. Please contact edYOU.',
                    'statusCode':402
                }
    else:
        return{
            'body':'No email found',
            'statusCode':402
        }
    
    
def checkemail(email):
    email=email.lower()
    data2 =user.get_item(Key={'email':email})
    if 'Item' in data2:
        data={
            'found':True,
            'data':data2['Item'],
            'role':'user'
            
        }
    else:
        data={
            'found':False
        }
    return data
