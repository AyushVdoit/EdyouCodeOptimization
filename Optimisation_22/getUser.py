import json
import boto3

# Create an instance of DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the 'user' and 'Token' tables from DynamoDB
user_table = dynamodb.Table('user')
token_table = dynamodb.Table('Token')


def token_checker(token):
    """
    Check if the provided token exists in the 'Token' table.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token exists, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in Data:
        return True
    else:
        return False


def lambda_handler(event, context):
    try:
        data = event
        required_fields = ["token"]

        # Check if all required fields are present in the request data
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if token_checker(event['token']):
            # Retrieve all users from the 'user' table
            response = user_table.scan()
            result = response['Items']

            # Paginate through the 'user' table if necessary
            while 'LastEvaluatedKey' in response:
                response = user_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])

            # Filter and sort the users based on their role
            user_list = []
            for user in result:
                if user['role'] == "User":
                    user_list.append(user)

            user_list.sort(key=lambda x: x['created_at'])

            if len(user_list) > 0:
                return {
                    'statusCode': 200,
                    'body': user_list
                }
            else:
                return {
                    'statusCode': 205,
                    'body': "No users are added yet"
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        # Handle any potential exceptions and return an error response
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
