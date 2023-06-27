import json
import boto3

# Initializing DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing 'user' table
user_table = dynamodb.Table('user')

# Accessing 'Token' table
token_table = dynamodb.Table('Token')

def token_checker(token):
    """
    Checks if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False

def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context: The runtime information of the Lambda function.

    Returns:
        dict: The response with status code, data, and body message.
    """
    try:
        if token_checker(event['token']):
            email = event['email']
            email = email.lower()
            data = user_table.get_item(Key={'email': email})
            
            if 'Item' in data:
                data['Item']["name"] = event["f_name"] + " " + event["l_name"]
                data['Item']['f_name'] = event['f_name']
                data['Item']['l_name'] = event['l_name']
                data['Item']['phone'] = event['phone']
                data['Item']['DOB'] = event['DOB']
                data['Item']['gender'] = event['gender']
                data['Item']['school'] = event['school']
                data['Item']['zip'] = event['zip']
                data['Item']['country'] = event['country']
                data['Item']['state'] = event['state']
                data['Item']['gpt3'] = event['gpt3']
                user_table.put_item(Item=data['Item'])
                return {
                    'statusCode': 200,
                    'data': data['Item'],
                    'body': 'Profile Updated'
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
