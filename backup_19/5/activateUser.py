import json
import boto3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  

def lambda_handler(event, context):
    # TODO implement
    if TokenChecker(event['token']):
        print(event)
        email = event['email'].lower()
        
        if event['status']=='Pending':
            resp=user.get_item(Key={'email' : email})
            data = resp['Item']
            data['status']="Active"
            user.put_item(Item=data)
            Email_sender(email,event['name'])
            return {
                'statusCode': 200,
                'body': 'activated successfully'
            }
            
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
# # <p>Your request has been approved, please login using your email and password.</p>
# <p>Kindly contact support in case of any issues.</p>
# <p>Thanks and Regards,<br>edYOU Team</p>
    
def Email_sender(email,name):
    sender_email ="edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"
    
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Access approved!"
    message["From"] = "edYOU Team"+"<"+sender_email+">"
    message["To"] = receiver_email
    html = """\
    <html>
        <body>
            <p>Hi """+name+""",</p>
            <p>Congratulations!</p>
            <p>We are pleased to inform you that your account has been approved!</p>
            <p>Please login to your account using your email and password.</p>
            <p><a href="https://uneequserdash.netlify.app/">Login to your Account</a></p>
            <p>In case of any issue kindly contact support team.</p>
            <p>Thanks and Regards,</p>
            <p>edYOU Team</p>
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