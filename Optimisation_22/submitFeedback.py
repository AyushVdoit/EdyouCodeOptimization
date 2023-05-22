import json  # Import the JSON module for handling JSON data
import boto3  # Import the Boto3 library for interacting with AWS services
from time import gmtime, strftime  # Import functions from the time module
from boto3.dynamodb.conditions import Key  # Import the Key class from the boto3.dynamodb.conditions module

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Investor', 'InvestorLoginHistory', and 'feedback' tables
user_table = dynamodb.Table("Investor")
investor_login_history_table = dynamodb.Table("InvestorLoginHistory")
feedback_table = dynamodb.Table("feedback")

def lambda_handler(event, context):
    # Get the current time in a specific format
    now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())

    # Retrieve the InvestorLoginHistory data from DynamoDB based on email and time
    investor_login_history_response = investor_login_history_table.get_item(Key={'email': event['email'], 'time': event['time']})
    investor_login_history_item = investor_login_history_response['Item']
    datanew = investor_login_history_item['data']
    last_five = datanew[-5:]

    # Prepare the data for the feedback item
    feedback_data = {
        "email": event['email'],
        "lastlogin": event['time'],
        "time": now,
        "data": last_five,
        "feedback": event['feedback'],
        "emoji": event['emoji'],
        "name": event['name'],
        "website": "Investor"
    }
    
    # Add the feedback item to the 'feedback' table
    feedback_table.put_item(Item=feedback_data)

    return {
        'statusCode': 200,
        'body': 'Feedback added'
    }
