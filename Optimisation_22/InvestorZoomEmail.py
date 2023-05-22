import json  # Import the JSON module for handling JSON data
import boto3  # Import the Boto3 library for interacting with AWS services
import os  # Import the OS module for accessing operating system functionality

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'Token' and 'Investor' tables
token_data_table = dynamodb.Table('Token')
investor_table = dynamodb.Table("Investor")

def lambda_handler(event, context):
    # Extract email and sessionID from the event payload
    email = event['email']
    session_id = event['sessionID']
    
    # Retrieve the Investor data from DynamoDB based on email
    data = investor_table.get_item(Key={'email': event['email'].lower()})
    
    # Update sessionID and token in the retrieved data
    data['Item']['sessionID'] = event['sessionID']
    data['Item']['token'] = event['token']
    
    # Update the Investor item in DynamoDB with the modified data
    investor_table.put_item(Item=data['Item'])
    
    return {
        'statusCode': 200,
        'body': "Session id saved"
    }
