import json  # Library for JSON operations
import smtplib  # Library for sending emails
import ssl  # Library for SSL (Secure Sockets Layer)
from email.mime.text import MIMEText  # Class for creating plain text email messages
from email.mime.multipart import MIMEMultipart  # Class for creating multipart email messages

def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data.
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response containing the status code and body.
    """
    email = event['email']
    name = event['name']
    password1 = event['password']
    send_email(email, name, password1)
    
    return {
        'statusCode': 200,
        'body': "Email sent"
    }

def send_email(email, name, password1):
    """
    Sends an email to the specified recipient.

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
    message["From"] = "edYOU Team" + " <" + sender_email + ">"
    message["To"] = receiver_email

    link = "https://devplatformsite.edyou.com/?q=AAMkADhhNzYyNDgxLTNkNGYtNDhiNS1iOWUzLTllMDBmMzEzOTA4MgBGAAAAAACvIW8tOruVQq_P-p9WUHDSBwC8MGg1BhiUTbxUOcauwKX2AAAAAAEMAAC8MGg1BhiUTbxUOcauwKX2AAKOYs4XAAA&email=" + receiver_email + "&password=" + password1 + "___Hellothere"
    
    html = """\
    <html>
        <body>
            <p>Hi """ + name + """,</p>
            <p>Welcome to the world of edYOU.</p>
            <p>I am Hannah, please click the link below to talk with me.<br><a href=""" + link + """>Click Here</a></p>
            <p>Kindly contact support in case of any issues.</p>
            <p>Regards,<br>Hannah<br>Human AI Avatar</p>
        </body>
    </html>
    """

    part3 = MIMEText(html, "html")

    message.attach(part3)

    # Create a secure connection with the server and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())