import json
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')


# Get DynamoDB tables
user = dynamodb.Table('Investor')
investor_login_history = dynamodb.Table('InvestorLoginHistory')
token_data = dynamodb.Table('Token')
token_data_prod = dynamodb.Table('Token_Prod')


# Function to check if token exists in Token_Data table
def TokenChecker(token):
    Data = token_data.get_item(Key={'token': token})
    if 'Item' in Data:
        return True
    else:
        return False


# Lambda handler function
def lambda_handler(event, context):
    if TokenChecker(event['token']):
        # TODO implement

        # Check if the login history exists for the given email and time
        Data = investor_login_history.get_item(
            Key={'email': event['email'].lower(), 'time': event['time']})

        if 'Item' in Data:
            now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
            time2 = datetime.strptime(now, '%Y-%m-%d,%H:%M:%S')
            time1 = datetime.strptime(event['time'], '%Y-%m-%d,%H:%M:%S')

            # Calculate the time difference
            time_diff = time2 - time1

            # Update the login history item with logout time and session duration
            Data['Item']['logout'] = now
            Data['Item']['Session'] = str(time_diff)
            investor_login_history.put_item(Item=Data['Item'])

            return {
                'statusCode': 200,
                'body': "logout"
            }
        else:
            return {
                'statusCode': 401,
                'body': 'Error'
            }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
