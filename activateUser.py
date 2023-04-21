import json
import boto3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

dynamodb = boto3.resource('dynamodb')
User=dynamodb.Table('user')
Token_Data = dynamodb.Table('Token')

def token_checker(token):
	data =Token_Data.get_item(Key={'token' : token})
	if 'Item' in data:
		return True
	else:
		return False  

# to activate the user and change user status to active
def lambda_handler(event, context):
	# if token is valid
	if token_checker(event['token']):
		email = event['email'].lower()
		if event['status']=='Pending':
			user_data=User.get_item(Key={'email' : email})
			user_info = user_data['Item']
			user_info['status']="Active"
			User.put_item(Item=user_info)
			email_sender(email,event['name'])
			return {
				'statusCode': 200,
				'body': 'User Activated Successfully'
			}
			
	else:
		return {
			'statusCode': 401,
			'body': 'Token is Invalid please re-login'
		}
# # <p>Your request has been approved, please login using your email and password.</p>
# <p>Kindly contact support in case of any issues.</p>
# <p>Thanks and Regards,<br>edYOU Team</p>
	
# send the email to reciever email address with account approval message
def email_sender(email,name):
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
	message_body = MIMEText(html, "html")
	message.attach(message_body)
	# Create secure connection with server and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(
			sender_email, receiver_email, message.as_string()
		)
	return