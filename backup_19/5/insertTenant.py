import json
import boto3
import smtplib, ssl
import requests
from time import gmtime, strftime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
default_region = "us-west-2"
ami_id = "ami-0d4d340c63d6308ca"
instance_type = "t3a.small"
instance_key_name = "rasa-node"
instance_sg_ids = ["sg-02fc68ab9a735b74e"]
subnetId = "subnet-0166be279739aaf6f"
dynamodb = boto3.resource('dynamodb')
user=dynamodb.Table('user')
Industries=dynamodb.Table('Industries')
Token_Data = dynamodb.Table('Token')
Investor = dynamodb.Table('Investor')
clientEc2 = boto3.client('ec2', region_name=default_region)
    
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        return False  
def lambda_handler(event, context):
    if TokenChecker(event['token']):
        email = event['email'].lower()
        resp=user.get_item(Key={'email' : email})
        # resp1=Investor.get_item(Key={'email' : email})
        event['email']=email
        if 'Item'in resp:
            return {
                'statusCode': 401,
                'body': 'email already exits.'
            }
        # elif 'Item'in resp1:
        #     return {
        #         'statusCode': 401,
        #         'body': 'email already exits.'
        #     }
            
        # print(event)
        else:
            token = event['token']
            del event['token']
            Data=Industries.get_item(Key={'id' : event['industry']})
            if 'Item' in Data:
                event['industryName']=Data['Item']['name']
                # event['']=Data['Item']['name']
                
            
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            event['name']=event['name']
            event['id']=uuid4().hex
            event['created_at']=now
            event['password']="sha256$HyukTkIMO8mbDTK3$954b8109130428a0baa041af8222879896c1d2524be7b9307dc68be4133b5f6d"
            uuid_inserted = uuid4().hex
            code=uuid_inserted
            # event['owner']="edyou"
            user_id=str(event['email'].lower())
            event['Time_out']=now
            # if event['gptPromptUser']=="":
            #     event['gptPromptUser']="Everything"
            event['Timeout_id']=uuid_inserted
            name = event['name']
            role = event['role']
            Email_sender(email,name,user_id,code,role)
            
            run_instance_response = clientEc2.run_instances(
                ImageId = ami_id,
                InstanceType = instance_type,
                KeyName = instance_key_name,
                SecurityGroupIds = instance_sg_ids,
                SubnetId = subnetId,
                # IamInstanceProfile,
                MaxCount = 1,
                MinCount = 1
            )
            run_instance_id = run_instance_response['Instances'][0]['InstanceId']
            run_instance_pvt_ip = run_instance_response['Instances'][0]['PrivateIpAddress']
            event['instance_id']=run_instance_id
            event['instance_pvt_ip']=run_instance_pvt_ip
            user.put_item(Item=event)
            
            return {
                'statusCode': 200,
                'body': "Tenant added successfully"
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
        link = "https://demo-admin-dev.netlify.app/setPassword?code="+code+"&user_id="+user_id+"___Hellothere"
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