import json  # JSON library for working with JSON data
import smtplib  # SMTP library for sending emails
import ssl  # SSL library for secure connections
from email.mime.text import MIMEText  # MIMEText class for creating text email messages
from email.mime.multipart import MIMEMultipart  # MIMEMultipart class for creating multipart email messages
import boto3  # Boto3 library for interacting with AWS services
from time import gmtime, strftime  # Functions for working with time
from datetime import datetime, timedelta  # Datetime library for working with dates and times

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
investor_table = dynamodb.Table('Investor_Prod')
token_data_table = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Check if the provided token is valid.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False


def lambda_handler(event, context):
    """
    Lambda handler function to update the investor.

    Args:
        event (dict): The event data.
        context: The runtime information.

    Returns:
        dict: The response with status code and body message.
    """
    if token_checker(event['token']):
        email = event['email'].lower()
        response = investor_table.get_item(Key={'email': email})
        if 'Item' in response:
            del event['token']
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            given_time = datetime.strptime(now, "%Y-%m-%d,%H:%M:%S")

            if event['gptPrompt'] == "":
                event['gptPrompt'] = "Everything"

            if response['Item']['expiredPassword']:

                if response['Item']['expire_time'] == event['expire_time']:
                    if event['expire_time'] == "" or event['expire_time'] == None:
                        event['expired_at'] = "2030-12-31,11:59:59"
                        event['expiredPassword'] = False
                    elif event['expire_time'] == 0:
                        event['expiredPassword'] = True
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at'] = final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword'] = False
                else:
                    if event['expire_time'] == "" or event['expire_time'] == None:
                        event['expired_at'] = "2030-12-31,11:59:59"
                        event['expiredPassword'] = False
                    elif event['expire_time'] == 0:
                        event['expiredPassword'] = True
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at'] = final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword'] = False
            else:
                if response['Item']['expire_time'] == event['expire_time']:
                    event['expiredPassword'] = response['Item']['expire_time']
                    if event['expire_time'] == "" or event['expire_time'] == None:
                        event['expired_at'] = "2030-12-31,11:59:59"
                        event['expiredPassword'] = False
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at'] = final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword'] = False
                else:
                    event['expiredPassword'] = False
                    if event['expire_time'] == "" or event['expire_time'] == None:
                        event['expired_at'] = "2030-12-31,11:59:59"
                    else:
                        final_time = given_time + timedelta(hours=int(event['expire_time']))
                        event['expired_at'] = final_time.strftime("%Y-%m-%d,%H:%M:%S")
                        event['expiredPassword'] = False

            if event['password'] != response['Item']['password']:
                link = "https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + email + "&password=" + event["password"] + "&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
                event['expiredPassword'] = False
                event["link"] = link
                email_sender(email, event['name'], event['password'])
                investor_table.put_item(Item=event)
            else:
                link = "https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + email + "&password=" + event["password"] + "&rq=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA___Hellothere"
                event["link"] = link
                investor_table.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': "Investor updated successfully"
        }


def email_sender(email, name, password1):
    """
    Send an email to the specified email address.

    Args:
        email (str): The recipient email address.
        name (str): The name of the recipient.
        password1 (str): The password.
    """
    sender_email = "edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to the world of edYOU!"
    message["From"] = "edYOU Team" + "<" + sender_email + ">"
    message["To"] = receiver_email

    link = "https://edyoudemo.netlify.app/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + receiver_email + "&password=" + password1 + "___Hellothere"
    html = """\
    <html>
        <body>
            <p>Hi """ + name + """,</p>
            <p>Welcome to the world of edYOU.</p>
            <p>I am Hannah, please click the link below to talk with me.<br><a href=""" + link + """>\>Click Here</a></p>
            <p>Kindly contact support in case of any issues.</p>
            <p>Regards,<br>Hannah<br>Human AI Avatar</p>
        </body>
    </html>
    """

    part3 = MIMEText(html, "html")

    message.attach(part3)

   # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    return
