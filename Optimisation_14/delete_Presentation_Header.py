import json  # Library for JSON handling
import boto3  # AWS SDK for Python (Boto3) for accessing AWS services

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB tables
presentation_table = dynamodb.Table('Presentation')
token_data_table = dynamodb.Table('Token')

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
        required_fields = ["id"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            if event['status'] == 'Inactive':
                for i in event['id']:
                    resp = presentation_table.get_item(
                        Key={
                            'id': i
                        }
                    )
                    resp['Item']['status'] = event['status']
                    presentation_table.put_item(Item=resp['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Learning deactivated successfully.'
                }
            elif event['status'] == 'Active':
                for i in event['id']:
                    resp = presentation_table.get_item(
                        Key={
                            'id': i
                        }
                    )
                    resp['Item']['status'] = event['status']
                    presentation_table.put_item(Item=resp['Item'])
                return {
                    'statusCode': 200,
                    'body': 'Learning activated successfully.'
                }
            elif event['status'] == 'Delete':
                for i in event['id']:
                    resp = presentation_table.get_item(
                        Key={
                            'id': i
                        }
                    )
                    resp['Item']['status'] = event['status']
                    presentation_table.put_item(Item=resp['Item'])

                    # resp = presentation_table.delete_item(Key={'id': i})
                return {
                    'statusCode': 200,
                    'body': 'Learning deleted successfully.'
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Error'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid. Please re-login.'
            }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }

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
