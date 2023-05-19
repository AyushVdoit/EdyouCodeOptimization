import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
Investor = dynamodb.Table('Investor')
token_data = dynamodb.Table('Token')
token_data_prod = dynamodb.Table('Token_Prod')

# Function to check if token exists in token_data or token_data_prod table


def token_checker(token):
    Data = token_data.get_item(Key={'token': token})
    if 'Item' in Data:
        return True
    else:
        Data = token_data_prod.get_item(Key={'token': token})
        if 'Item' in Data:
            return True
        else:
            return False

# Lambda handler function
def lambda_handler(event, context):
    try:
        data = event
        required_fields = ["token"]

        # Check if required fields are present in the request data
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        # Check if token is valid
        if token_checker(event['token']):
            # Fetch data from the 'Investor' table based on email
            Data = Investor.get_item(Key={'email': event['email'].lower()})
            if 'Item' in Data:
                return {
                    'statusCode': 200,
                    'body': Data['Item']
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
