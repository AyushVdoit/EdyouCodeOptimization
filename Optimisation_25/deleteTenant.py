import json
import boto3

default_region = "us-west-2"

# Initializing the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing the 'user' table in DynamoDB
user = dynamodb.Table('user')

# Accessing the 'Topic' table in DynamoDB
topic_table = dynamodb.Table('Topic')

# Accessing the 'Investor' table in DynamoDB
investor_table = dynamodb.Table('Investor')

# Accessing the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

# Accessing the 'Question' table in DynamoDB
question_table = dynamodb.Table('Question')

# Creating an EC2 client
client_ec2 = boto3.client('ec2', region_name=default_region)

# Function to check the validity of a token in the Token table
def token_checker(token):
    """
    Checks the validity of a token in the Token table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

# AWS Lambda function handler
def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Context object representing the runtime information.

    Returns:
        dict: Response data to be returned by the Lambda function.
    """
    try:
        data = event
        required_fields = ["token", "email", "status"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            email = event['email'].lower()

            if event['status'] == 'Delete':
                resp = user.get_item(Key={'email': email})
                if 'Item' in resp:
                    instance_id = resp['Item']['instance_id']

                # Update status to "Delete" in the Topic table for matching Tenantemail
                response = topic_table.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = topic_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])
                for i in result:
                    if event['email'] == i['Tenantemail']:
                        if i['status'] == "Active":
                            i['status'] = "Delete"
                            topic_table.put_item(Item=i)

                # Update status to "Delete" in the Question table for matching Tenantemail
                response = question_table.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = question_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])
                for i in result:
                    if event['email'] == i['Tenantemail']:
                        if i['status'] == "Active":
                            i['status'] = "Delete"
                            question_table.put_item(Item=i)

                # Delete users with the role "User" and matching tenantEmail
                response = user.scan()
                result = response['Items']
                while 'LastEvaluatedKey' in response:
                    response = user.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    result.extend(response['Items'])

                user_list = []
                for i in result:
                    if i['role'] == "User":
                        user_list.append(i)

                for i in user_list:
                    if event['email'] == i['tenantEmail']:
                        response = user.delete_item(
                            Key={
                                'email': i['email'],
                            },
                        )

                # Delete the matching record from the Investor table
                response = investor_table.delete_item(
                    Key={
                        'email': email,
                    },
                )

                # Delete the matching record from the user table
                response = user.delete_item(
                    Key={
                        'email': email,
                    },
                )

                # Terminate the EC2 instance
                client_ec2.terminate_instances(InstanceIds=[instance_id])

                return {
                    'statusCode': 200,
                    'body': 'Tenant deleted successfully'
                }
            else:
                return {
                    'statusCode': 401,
                    'body': 'done'
                }

        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
