import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
import smtplib  # Library for sending emails using SMTP
import ssl  # Library for creating secure connections
from time import gmtime, strftime  # Library for working with time
from email.mime.text import MIMEText  # Library for creating plain text email messages
from email.mime.multipart import MIMEMultipart  # Library for creating multipart email messages
from uuid import uuid4  # Library for generating UUIDs

# Create an instance of DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'user' and 'Token' tables from DynamoDB
user_table = dynamodb.Table('user')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response object.
    """
    print(event)
    data = event
    required_fields = ["token"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
                'statusCode': 400,
                'body': f'Error: {field} is required and cannot be empty'
            }
    
    if token_checker(event['token']):
        email = event['email'].lower()
        resp = user_table.get_item(Key={'email': email})
        if 'Item' in resp:
            return {
                'statusCode': 401,
                'body': 'Email already exists.'
            }
        else:
            del event['token']
            if event['emailbyUser'] in ['admin@edyou.com', 'admin@edyou.in']:
                if event['tenantEmail'] == "":
                    event['emailbyUser'] = ""
                else:
                    event['emailbyUser'] = event['tenantEmail']
            
            if event['emailbyUser'] != "":
                data = user_table.get_item(Key={'email': event['emailbyUser'].lower()})
                if 'Item' in data:
                    event['tenantName'] = data['Item']['name']
                
            
            else:
                event['tenantName'] = ""
            event['tenantEmail']= event['emailbyUser']
            del event['emailbyUser']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            event['name'] = event['f_name'] + " " + event['l_name']
            event['id'] = uuid4().hex
            event['created_at'] = now
            uuid_inserted = uuid4().hex
            code = uuid_inserted
            event['owner'] = "edyou"
            user_id = str(event['email'].lower())
            event['Time_out'] = now
            
            if event['gptPromptUser'] == "":
                event['gptPromptUser'] = "Everything"
            
            event['Timeout_id'] = uuid_inserted
            name = event['name']
            role = event['role']
            email_sender(email, name, user_id, code, role)
            
            user_table.put_item(Item=event)
            
            return {
                'statusCode': 200,
                'body': "User added successfully"
            }
            
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid, please re-login'
        }

def email_sender(email, name, user_id, code, role):
    """
    Send an email to the specified email address.

    Args:
        email (str): The recipient's email address.
        name (str): The recipient's name.
        user_id (str): The user ID.
        code (str): The code for password reset.
        role (str): The role of the user.

    Returns:
        None
    """
    sender_email = "edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Set your password"
    message["From"] = "edYOU Team" + "<" + sender_email + ">"
    message["To"] = receiver_email

    if role == 'User':
        link = "https://demo-med-dev.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"
    else:
        link = "https://admindevelopment.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"

    html = f"""
    <html>
        <body>
            <p>Hi {name},</p>
            <p>Please click the link below to reset your password.<br><a href="{link}">Click Here</a><br>The link will be available for 10 minutes only. </p>
            <p>Kindly contact us in case of any query.</p>
            <p>Thanks and Regards,<br>edYOU Team</p>
        </body>
    </html>
    """
# Turn these into plain/html MIMEText objects
    part3 = MIMEText(html, "html")
    message.attach(part3)
    
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
