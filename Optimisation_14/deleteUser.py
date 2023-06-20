import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
user_table = dynamodb.Table('user')
token_data_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Check if the token is valid.

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
    Lambda handler function to handle the AWS Lambda event.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object representing the runtime information.

    Returns:
        dict: The response containing the HTTP status code and body.

    Raises:
        Exception: Any exception that occurs during the execution of the Lambda function.
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
            print(event)
            email = event['email'].lower()

            if event['status'] == 'Delete':
                response = user_table.delete_item(
                    Key={
                        'email': email,
                    },
                )
                if "role" in event:
                    msg = event['role']
                else:
                    msg = "User"
                return {
                    'statusCode': 200,
                    'body': f'{msg} deleted successfully'
                }
            elif event['status'] == "Deactivate":
                resp = user_table.get_item(Key={'email': email})
                data = resp['Item']
                data['status'] = "Inactive"
                user_table.put_item(Item=data)
                return {
                    'statusCode': 401,
                    'body': 'Deactivate successfully'
                }
            elif event['status'] == "Activate":
                resp = user_table.get_item(Key={'email': email})
                data = resp['Item']
                data['status'] = "Active"
                user_table.put_item(Item=data)
                return {
                    'statusCode': 401,
                    'body': 'Activate successfully'
                }
            else:
                return {
                    'statusCode': 401,
                    'body': 'done'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid. Please re-login.'
            }
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
