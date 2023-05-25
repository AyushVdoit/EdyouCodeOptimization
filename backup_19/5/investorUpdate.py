import json
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from time import gmtime, strftime
from datetime import datetime, timedelta
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor_Prod')
Token_Data = dynamodb.Table('Token_Prod')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False
def lambda_handler(event, context):
    if TokenChecker(event['token']):
        email = event['email'].lower()
        resp=Investor.get_item(Key={'email' : email})
        if 'Item'in resp:
            del event['token']
            # event['expired_at']=resp['Item']['expired_at']
            # event['firstTime']=resp['Item']['firstTime']
            # event['StartTestSeries']=resp['Item']['StartTestSeries']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            given_time = datetime.strptime(now, "%Y-%m-%d,%H:%M:%S")
                
            if event['gptPrompt']=="":
                event['gptPrompt']="Everything"
            if resp['Item']['expiredPassword']==True:
                # print(resp['Item']['expire_time'])
                
                if resp['Item']['expire_time']==event['expire_time']:
                    # event['expiredPassword']=True
                    if event['expire_time']=="" or event['expire_time']==None:
                        print('yes')
                        event['expired_at']="2030-12-31,11:59:59"
                        event['expiredPassword']=False
                    elif event['expire_time']==0:
                        
                        # final_time = given_time + timedelta(hours=int(event['expire_time']))
                        # event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=True
                        print('yes')
                    else:
                        
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=False
                else:
                    if event['expire_time']=="" or event['expire_time']==None:
                        event['expired_at']="2030-12-31,11:59:59"
                        event['expiredPassword']=False
                    elif event['expire_time']==0:
                        
                        # final_time = given_time + timedelta(hours=int(event['expire_time']))
                        # event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=True
        
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=False
            else:
                if resp['Item']['expire_time']==event['expire_time']:
                    event['expiredPassword']=resp['Item']['expire_time']
                    if event['expire_time']=="" or event['expire_time']==None:
                        event['expired_at']="2030-12-31,11:59:59"
                        event['expiredPassword']=False
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=False
                else:
                    event['expiredPassword']=False
                    if event['expire_time']=="" or event['expire_time']==None:
                        event['expired_at']="2030-12-31,11:59:59"
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at']=final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword']=False
                # event['expiredPassword']=False
                
            if event['password']!=resp['Item']['password']:
                link="https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email="+email+"&password="+event["password"]+"&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
                event['expiredPassword']=False
                event["link"]=link
                Email_sender(email,event['name'],event['password'])
                Investor.put_item(Item=event)
            else:
                link="https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email="+email+"&password="+event["password"]+"&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
                event["link"]=link
                Investor.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Investor updated successfully"
        }

    
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
    link="https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email="+receiver_email+"&password="+password1+"___Hellothere"
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