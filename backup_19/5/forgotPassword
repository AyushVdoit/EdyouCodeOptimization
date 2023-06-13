import json
import boto3
import uuid
import secrets
from boto3.dynamodb.conditions import Key
import urllib
from time import gmtime, strftime
import string
import random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
def lambda_handler(event, context):
    email=event['email'].lower()
    data = user.get_item(Key={'email':email})
    if 'Item' in data:
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        uuid_inserted = uuid.uuid4().hex
        code=uuid_inserted
        line = data['Item']
        user_id=str(line['email'])
        line['Time_out']=now
        line['Timeout_id']=uuid_inserted
        name = line['name']
        role = line['role']
        Email_sender(event['email'],name,user_id,code,role)
        user.put_item(Item=line)
        
        return {
                'statusCode': 200,
                'message': 'The reset password link has been sent to your email.',
                'line':line
            }
        
    
        
    else:
        return{
            'message':'Error! No email found',
            'statusCode':401
        }




def Email_sender(email,name,user_id,code,role):
    sender_email ="edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"
    
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset your password "
    message["From"] = "edYOU Team"+"<"+sender_email+">"
    message["To"] = receiver_email
    if role =='User':
    # link="http://edyoutechnologies.s3-website-us-west-2.amazonaws.com/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
        link ="https://uneequserdash.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
    elif role =="Tenant":
        link="https://demo-admin-dev.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
    else:
        link = "https://uneeqadmindash.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
    html = """\
    <html>
        <body>
            <p>Hi """+name+""",</p>
            <p>Please click the link below to reset your password.<br><a href="""+link+"""\>Click Here</a><br>The link will be available for 10 minutes only. </p>
            <p>Kindly contact us in case of any query.</p>
        
            <p>Thanks and Regards,<br>edYOU Team</p>
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