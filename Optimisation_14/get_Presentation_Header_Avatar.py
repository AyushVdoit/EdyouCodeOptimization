import json
import boto3

# Importing required libraries
# Importing JSON library for handling JSON data
import json
# Importing Boto3 library for interacting with AWS services
import boto3

# Creating DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing the Presentation table in DynamoDB
presentation_table = dynamodb.Table('Presentation')
# Accessing the Investor table in DynamoDB
user_table = dynamodb.Table("Investor")
# Accessing the Token table in DynamoDB
token_table = dynamodb.Table('Token')

def token_checker(email, token):
    """
    Check if the provided token is valid for the given email.

    Args:
        email (str): The email associated with the token.
        token (str): The token to be checked.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    # Retrieve the token data from the Token table
    token_data = token_table.get_item(Key={'token': token})
    if 'Item' in token_data:
        # Retrieve the user data from the Investor table
        user_data = user_table.get_item(Key={'email': email})
        if 'Item' in user_data:
            # Check if the token matches the one stored in the user data
            if user_data['Item']['token'] == token:
                return True
            else:
                return False
        else:
            return False
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: The response containing the status code and body.
    """
    try:
        # Extract the data from the event
        data = event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['email'].lower(), event['token']):
            # Retrieve all items from the Presentation table
            response = presentation_table.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = presentation_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            tenant_list = []
            admin_list = []
            if event['Tenantemail'] == "":
                # Filter admin items
                for item in result:
                    if item['Tenantemail'] == "":
                        if item['status'] == "Active":
                            if item['URL'] != "":
                                admin_list.append(item)
            else:
                # Filter tenant items
                for item in result:
                    if event['Tenantemail'] == item['Tenantemail']:
                        if item['status'] == "Active":
                            if item['URL'] != "":
                                tenant_list.append(item)
                    elif item['Tenantemail'] != "":
                        pass
            if event['Tenantemail'] == "":
                return {
                    "list": "Admin",
                    'statusCode': 200,
                    'body': admin_list
                }
            elif event['Tenantemail'] != "":
                return {
                    "list": "Tenant",
                    'statusCode': 200,
                    'body': tenant_list
                }
            else:
                return {
                    'statusCode': 205,
                    'body': "No test series are added yet"
                }
        else:
            return {
                'statusCode': 401,
                'body': 'You have logged in from another device, please close from that device and re-login to continue.'
            }
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
