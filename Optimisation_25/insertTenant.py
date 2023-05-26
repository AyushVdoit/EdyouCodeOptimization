import json  # JSON manipulation
import boto3  # AWS SDK for Python
import smtplib  # SMTP email sending
import ssl  # SSL certificate handling
import requests  # HTTP requests
from time import gmtime, strftime  # Time manipulation
from email.mime.text import MIMEText  # Email MIME text handling
from email.mime.multipart import MIMEMultipart  # Email MIME multipart handling
from uuid import uuid4  # UUID generation

default_region = "us-west-2"  # Default AWS region
ami_id = "ami-0d4d340c63d6308ca"  # EC2 AMI ID
instance_type = "t3a.small"  # EC2 instance type
instance_key_name = "rasa-node"  # EC2 instance key name
instance_sg_ids = ["sg-02fc68ab9a735b74e"]  # EC2 security group IDs
subnet_id = "subnet-0166be279739aaf6f"  # Subnet ID

dynamodb = boto3.resource('dynamodb')  # DynamoDB resource
user_table = dynamodb.Table('user')  # User table in DynamoDB
industries_table = dynamodb.Table('Industries')  # Industries table in DynamoDB
token_data_table = dynamodb.Table('Token')  # Token Data table in DynamoDB
investor_table = dynamodb.Table('Investor')  # Investor table in DynamoDB
client_ec2 = boto3.client('ec2', region_name=default_region)  # EC2 client

def token_checker(token):
    """
    Check if the token is valid by looking it up in the Token Data table.

    Args:
        token (str): Token string to check.

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
    AWS Lambda handler function.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): AWS Lambda function context.

    Returns:
        dict: Response object containing the status code and body.
    """
    if token_checker(event['token']):
        email = event['email'].lower()
        resp = user_table.get_item(Key={'email': email})

        event['email'] = email
        if 'Item' in resp:
            return {
                'statusCode': 401,
                'body': 'Email already exists.'
            }

        token = event['token']
        del event['token']
        data = industries_table.get_item(Key={'id': event['industry']})
        if 'Item' in data:
            event['industry_name'] = data['Item']['name']

        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        event['name'] = event['name']
        event['id'] = uuid4().hex
        event['created_at'] = now
        event['password'] = "sha256$HyukTkIMO8mbDTK3$954b8109130428a0baa041af8222879896c1d2524be7b9307dc68be4133b5f6d"
        uuid_inserted = uuid4().hex
        code = uuid_inserted
        user_id = str(event['email'].lower())
        event['time_out'] = now
        event['timeout_id'] = uuid_inserted
        name = event['name']
        role = event['role']
        email_sender(email, name, user_id, code, role)

        run_instance_response = client_ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=instance_key_name,
            SecurityGroupIds=instance_sg_ids,
            SubnetId=subnet_id,
            MaxCount=1,
            MinCount=1
        )
        run_instance_id = run_instance_response['Instances'][0]['InstanceId']
        run_instance_pvt_ip = run_instance_response['Instances'][0]['PrivateIpAddress']
        event['instance_id'] = run_instance_id
        event['instance_pvt_ip'] = run_instance_pvt_ip
        user_table.put_item(Item=event)

        return {
            'statusCode': 200,
            'body': "Tenant added successfully"
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid. Please re-login.'
        }

def email_sender(email, name, user_id, code, role):
    """
    Send an email to the specified email address with a password reset link.

    Args:
        email (str): Email address of the recipient.
        name (str): Name of the recipient.
        user_id (str): User ID for the password reset link.
        code (str): Code for the password reset link.
        role (str): Role of the user.

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
        link = "https://demo-admin-dev.netlify.app/setPassword?code=" + code + "&user_id=" + user_id + "___Hellothere"

    html = """
    <html>
        <body>
            <p>Hi """ + name + """,</p>
            <p>Please click the link below to reset your password.<br><a href=""" + link + """>\Click Here</a><br>The link will be available for 10 minutes only. </p>
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
        server.sendmail(sender_email, receiver_email, message.as_string())

    return
