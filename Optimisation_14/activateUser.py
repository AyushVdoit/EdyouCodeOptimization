import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
import smtplib  # Library for sending emails
import ssl  # Library for SSL (Secure Sockets Layer) functionality
from email.mime.text import MIMEText  # Library for creating email message bodies
from email.mime.multipart import MIMEMultipart  # Library for creating multipart email messages

# Create a connection to DynamoDB service
dynamodb = boto3.resource('dynamodb')

# Access the 'user' table in DynamoDB
user_table = dynamodb.Table('user')

# Access the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

# Function to check if a token is valid
def token_checker(token):
    """
    Checks if the token is valid.

    Args:
        token (str): Token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    response = token_table.get_item(Key={'token': token})
    if 'Item' in Data:
        return True
    else:
        return False 

# Lambda function handler
def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): Event data.
        context: Context data.

    Returns:
        dict: Response containing status code and body.
    """
    if token_checker(event['token']):
        print(event)
        email = event['email'].lower()
        
        if event['status'] == 'Pending':
            response = user_table.get_item(Key={'email': email})
            data = response['Item']
            data['status'] = "Active"
            user_table.put_item(Item=data)
            send_activation_email(email, event['name'])
            return {
                'statusCode': 200,
                'body': 'Activated successfully'
            }
            
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid, please re-login'
        }

# Function to send an activation email
def send_activation_email(email, name):
    """
    Sends an activation email to the user.

    Args:
        email (str): Email address of the user.
        name (str): Name of the user.

    Returns:
        None
    """
    sender_email = "edyoutechnologies@gmail.com"
    receiver_email = email
    password = "dbhgpcqhjuhvtiro"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Access approved!"
    message["From"] = "edYOU Team" + "<" + sender_email + ">"
    message["To"] = receiver_email
    html = """\
    <html>
        <body>
            <p>Hi """ + name + """,</p>
            <p>Congratulations!</p>
            <p>We are pleased to inform you that your account has been approved!</p>
            <p>Please login to your account using your email and password.</p>
            <p><a href="https://uneequserdash.netlify.app/">Login to your Account</a></p>
            <p>In case of any issue kindly contact the support team.</p>
            <p>Thanks and Regards,</p>
            <p>edYOU Team</p>
        </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)
    print(message)
    
    # Create secure connection with the server and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    return

