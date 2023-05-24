import json
import boto3
import smtplib, ssl
from time import gmtime, strftime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
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
        resp=user.get_item(Key={'email' : email})
        if 'Item'in resp:
            return {
                'statusCode': 401,
                'body': 'email already exits.'
            }
        # print(event)
        else:
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
                    
            else:
                event['tenantName']=""
            event['tenantEmail']= event['emailbyUser']
            del event['emailbyUser']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            event['name']=event['f_name']+" "+event['l_name']
            event['id']=uuid4().hex
            event['created_at']=now
            uuid_inserted = uuid4().hex
            code=uuid_inserted
            event['owner']="edyou"
            user_id=str(event['email'].lower())
            event['Time_out']=now
            if event['gptPromptUser']=="":
                event['gptPromptUser']="Everything"
            event['Timeout_id']=uuid_inserted
            name = event['name']
            role = event['role']
            Email_sender(email,name,user_id,code,role)
            
            user.put_item(Item=event)
            return {
                'statusCode': 200,
                'body': "User added successfully"
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
    
def Email_sender(email,name,user_id,code,role):
    sender_email ="edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"
    
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Set your password"
    message["From"] = "edYOU Team"+"<"+sender_email+">"
    message["To"] = receiver_email
    if role =='User':
    # link="http://edyoutechnologies.s3-website-us-west-2.amazonaws.com/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
        link ="https://demo-med-dev.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
    else:
        link = "https://admindevelopment.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
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