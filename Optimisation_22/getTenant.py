import json  # Import the JSON module for working with JSON data
import boto3  # Import the Boto3 library for interacting with AWS services

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'user' table from DynamoDB
user_table = dynamodb.Table('user')

# Get the 'Token' table from DynamoDB
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the given token is valid.

    Args:
        token (str): The token to check.

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
    Lambda handler function.

    Args:
        event (dict): The event data.
        context (object): The context object.

    Returns:
        dict: The response containing the statusCode and body.
    """
    try:
        data = event
        required_fields = ["token"]
        
        # Check if the required fields are present and not empty
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if token_checker(event['token']):
            # Scan the 'user' table to retrieve all items
            response = user_table.scan()
            result = response['Items']
            
            # Continue scanning if there are more items
            while 'LastEvaluatedKey' in response:
                response = user_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            
            l = [] # assign a proper variable name for l[]
            # dici={} no use of this dictionary
            
            # Filter the items based on role
            for item in result:
                if item['role'] == "Tenant":
                    l.append(item)
            
            # Sort the items by 'created_at' in ascending order
            l.sort(key=lambda x: x['created_at'])
            
            if len(l) > 0:
                return {
                    'statusCode': 200,
                    'body': l
                }
            else:
                return {
                    'statusCode': 205,
                    'body': "No users are added yet"
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
