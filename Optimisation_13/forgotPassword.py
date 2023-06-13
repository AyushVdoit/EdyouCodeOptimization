import json  # Import JSON module for handling JSON data
import boto3  # Import Boto3 library for interacting with AWS services
import uuid  # Import UUID module for generating unique IDs
import secrets  # Import Secrets module for generating secure random numbers
from boto3.dynamodb.conditions import Key  # Import Key from boto3.dynamodb.conditions module
import urllib  # Import urllib module for URL encoding and decoding
from time import gmtime, strftime  # Import gmtime and strftime from time module
import string  # Import string module for working with strings
import random  # Import random module for generating random values
import smtplib  # Import smtplib module for sending emails
import ssl  # Import ssl module for secure connections
from email.mime.text import MIMEText  # Import MIMEText from email.mime.text module
from email.mime.multipart import MIMEMultipart  # Import MIMEMultipart from email.mime.multipart module

dynamodb = boto3.resource('dynamodb')  # Create a DynamoDB resource object
user_table = dynamodb.Table('user')  # Get the user table

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object provided by Lambda.

    Returns:
        dict: The response object.
    """
    email = event['email'].lower()

    # Get user data from the user table using email
    data = user_table.get_item(Key={'email': email})

    if 'Item' in data:
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        uuid_inserted = uuid.uuid4().hex
        code = uuid_inserted
        line = data['Item']
        user_id = str(line['email'])
        line['Time_out'] = now
        line['Timeout_id'] = uuid_inserted
        name = line['name']
        role = line['role']
        Email_sender(event['email'], name, user_id, code, role)
        user_table.put_item(Item=line)
        
        return {
            'statusCode': 200,
            'message': 'The reset password link has been sent to your email.',
            'line': line
        }
    else:
        return {
            'message': 'Error! No email found',
            'statusCode': 401
        }

def Email_sender(email, name, user_id, code, role):
    """
    Send email with password reset link.

    Args:
        email (str): The recipient email address.
        name (str): The recipient name.
        user_id (str): The user ID.
        code (str): The reset code.
        role (str): The user role.

    Returns:
        None
    """
    sender_email = "edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset your password"
    message["From"] = "edYOU Team" + "<" + sender_email + ">"
    message["To"] = receiver_email

    if role == 'User':
        link = "https://uneequserdash.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"
    elif role == "Tenant":
        link = "https://demo-admin-dev.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"
    else:
        link = "https://uneeqadmindash.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"

    html = """\
    <html>
        <body>
            <p>Hi """ + name + """,</p>
            <p>Please click the link below to reset your password.<br><a href=""" + link + """>\>Click Here</a><br>The link will be available for 10 minutes only. </p>
            <p>Kindly contact us in case of any query.</p>
        
            <p>Thanks and Regards,<br>edYOU Team</p>
        </body>
    </html>
    """    

    part3 = MIMEText(html, "html")
    message.attach(part3)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    return
