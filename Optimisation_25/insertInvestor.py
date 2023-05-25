import json  # JSON library for working with JSON data
import boto3  # Boto3 library for interacting with AWS services
import smtplib  # SMTP library for sending emails
import ssl  # SSL library for secure connections
from time import gmtime, strftime  # Functions for working with time
from datetime import datetime, timedelta  # Datetime library for working with dates and times
from email.mime.text import MIMEText  # MIMEText class for creating text email messages
from email.mime.multipart import MIMEMultipart  # MIMEMultipart class for creating multipart email messages
from uuid import uuid4  # UUID library for generating unique identifiers

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# DynamoDB tables
investor_table = dynamodb.Table('Investor')
user_table = dynamodb.Table('user')
token_data_table = dynamodb.Table('Token')
token_data_prod_table = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Check if the token is valid.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        data = token_data_prod_table.get_item(Key={'token': token})
        if 'Item' in data:
            return True
        else:
            return False


def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data.
        context: The context object.

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
        resp = investor_table.get_item(Key={'email': email})
        if 'Item' in resp:
            return {
                'statusCode': 401,
                'body': 'Email already exists.'
            }
        resp = user_table.get_item(Key={'email': email})
        if 'Item' in resp:
            if resp['Item']['role'] != "Tenant":
                return {
                    'statusCode': 401,
                    'body': 'Email already exists.'
                }
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
                event['instance_id'] = data['Item']['instance_id']
                event['instance_pvt_ip'] = data['Item']['instance_pvt_ip']
        else:
            event['tenantName'] = ""
            event['instance_id'] = "i-074868ffc377ca92f"
            event['instance_pvt_ip'] = "172.31.53.209"

        event['tenantEmail'] = event['emailbyUser']
        del event['emailbyUser']

        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        event['name'] = event['f_name'] + " " + event['l_name']
        event['id'] = uuid4().hex
        event['created_at'] = now
        given_time = datetime.strptime(now, "%Y-%m-%d,%H:%M:%S")
        if event['expire_time'] == "" or event['expire_time'] is None:
            event['expired_at'] = "2030-12-31,11:59:59"
        else:
            final_time = given_time + timedelta(hours=int(event['expire_time']))
            event['expired_at'] = final_time.strftime("%Y-%m-%d,%H:%M:%S")
        event['expiredPassword'] = False
        uuid_inserted = uuid4().hex
        event['firstTime'] = True
        event['StartTestSeries'] = False
        event['Time_out'] = now
        if event['gptPrompt'] == "":
            event['gptPrompt'] = "Everything"
        event['Timeout_id'] = uuid_inserted
        name = event['name']
        email_sender(email, name, event['password'])
        link = "https://demo-inv-dev.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + email + "&password=" + event["password"] + "&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
        event['link'] = link
        investor_table.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Investor added successfully"
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid. Please re-login.'
        }


def email_sender(email, name, password1):
    """
    Send an email to the specified recipient.

    Args:
        email (str): The recipient's email address.
        name (str): The recipient's name.
        password1 (str): The password.

    Returns:
        None
    """
    sender_email = "edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to the world of edYOU!"
    message["From"] = "edYOU Team" + "<" + sender_email + ">"
    message["To"] = receiver_email

    link = "https://demo-inv-dev.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + receiver_email + "&password=" + password1 + "___Hellothere"
    html = f"""
    <html>
        <body>
            <p>Hi {name},</p>
            <p>Welcome to the world of edYOU.</p>
            <p>I am Hannah, please click the link below to talk with me.<br><a href="{link}">Click Here</a></p>
            <p>Kindly contact support in case of any issues.</p>
            <p>Regards,<br>Hannah<br>Human AI Avatar</p>
        </body>
    </html>
    """

    part3 = MIMEText(html, "html")
    message.attach(part3)

    # Create secure connection with the server and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
