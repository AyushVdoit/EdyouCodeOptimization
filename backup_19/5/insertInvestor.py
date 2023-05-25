import json
import boto3
import smtplib, ssl
from time import gmtime, strftime
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
# client = boto3.client('events')
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')
from werkzeug.security import generate_password_hash
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
    # try:
    print(event)
    data =event
    required_fields = ["token"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
            'statusCode': 400,
            'body': f'Error: {field} is required and cannot be empty'
            }
    if TokenChecker(event['token']):
        email = event['email'].lower()
        resp=Investor.get_item(Key={'email' : email})
        if 'Item'in resp:
            return {
                'statusCode': 401,
                'body': 'email already exits.'
            }
        resp=user.get_item(Key={'email' : email})
        if 'Item'in resp:
            if resp['Item']['role']!="Tenant":
                return {
                    'statusCode': 401,
                    'body': 'email already exits.'
                }
        # print(event)

        del event['token']
        if event['emailbyUser'] in ['admin@edyou.com','admin@edyou.in']:
            if event['tenantEmail']=="":
                event['emailbyUser']=""
            else:
                event['emailbyUser']=event['tenantEmail']
        if event['emailbyUser']!="":
            Data=user.get_item(Key={'email' : event['emailbyUser'].lower()})
            if 'Item' in Data:
                event['tenantName']=Data['Item']['name']
                event['instance_id']=Data['Item']['instance_id']
                event['instance_pvt_ip']=Data['Item']['instance_pvt_ip']
        
        else:
            event['tenantName']=""
            event['instance_id']="i-074868ffc377ca92f"
            event['instance_pvt_ip']="172.31.53.209"
        
        event['tenantEmail']= event['emailbyUser']
        del event['emailbyUser']
    
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        event['name']=event['f_name']+" "+event['l_name']
        event['id']=uuid4().hex
        event['created_at']=now
        given_time = datetime.strptime(now, "%Y-%m-%d,%H:%M:%S")
        if event['expire_time']=="" or event['expire_time']==None:
            event['expired_at']="2030-12-31,11:59:59"
        else:
            final_time = given_time + timedelta(hours=int(event['expire_time']))
            event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
        event['expiredPassword']=False
        uuid_inserted = uuid4().hex
        event['firstTime']=True
        event['StartTestSeries']=False
        event['Time_out']=now
        if event['gptPrompt']=="":
            event['gptPrompt']="Everything"
        event['Timeout_id']=uuid_inserted
        name = event['name']
        Email_sender(email,name,event['password'])
        link="https://demo-inv-dev.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email="+email+"&password="+event["password"]+"&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
        event['link']=link
        Investor.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Investor added successfully"
        }
            
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
    
    # except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError,json.JSONDecodeError, SyntaxError ) as e:
    #     return {
    #         'statusCode': 400,
    #         'body': f'Error: {e}'
    #     }
    
def Email_sender(email,name,password1):
    sender_email ="edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"
    
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to the world of edYOU!"
    message["From"] = "edYOU Team"+"<"+sender_email+">"
    message["To"] = receiver_email
    # if role =='Investor':
        # link ="https://uneeqInvestordash.netlify.app/setPassword?code="+code+"&Investor_id="+Investor_id+"___Hellothere"
    link="https://demo-inv-dev.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email="+receiver_email+"&password="+password1+"___Hellothere"
    html = """\
    <html>
        <body>
            <p>Hi """+name+""",</p>
            <p>Welcome to the world of edYOU.</p>
            <p>I am Hannah, please click the link below to talk with me.<br><a href="""+link+"""\>Click Here</a></p>
            <p>Kindly contact support in case of any issues.</p>
            <p>Regards,<br>Hannah<br>Human AI Avatar</p>

        </body>
    </html>
    """    
    # Turn these into plain/html MIMEText objects
    
    part3 = MIMEText(html, "html")
    

    message.attach(part3)
    print(message)
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    return