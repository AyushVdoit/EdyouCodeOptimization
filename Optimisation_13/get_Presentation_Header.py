import json  # Import JSON module for handling JSON data
import boto3  # Import Boto3 library for interacting with AWS services

dynamodb = boto3.resource('dynamodb')  # Create a DynamoDB resource object
presentation_table = dynamodb.Table('Presentation')  # Get the presentation table
token_table = dynamodb.Table('Token')  # Get the token table

def TokenChecker(token):
    """
    Check if the token exists in the token table.

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
    Lambda function handler.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object provided by Lambda.

    Returns:
        dict: The response object.
    """
    try:
        data = event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }

        if TokenChecker(event['token']):
            response = presentation_table.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = presentation_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])

            tenant_list = []
            admin_list = []

            if 'email' not in event:
                event['email'] = ""
                event['role'] = ""

            for item in result:
                if event['email'] == item['Tenantemail']:
                    tenant_dict = {
                        'id': item['id'],
                        'description': item['description'],
                        'title': item['title'],
                        'Tenantemail': item['Tenantemail'],
                        'name': item['name'],
                        'status': item['status'],
                        'created_at': item['created_at'],
                        'URL': item['URL']
                    }
                    tenant_list.append(tenant_dict)

                if event['role'] == "Admin":
                    admin_dict = {
                        'id': item['id'],
                        'description': item['description'],
                        'title': item['title'],
                        'Tenantemail': item['Tenantemail'],
                        'name': item['name'],
                        'status': item['status'],
                        'created_at': item['created_at'],
                        'URL': item['URL']
                    }
                    admin_list.append(admin_dict)

            if event['role'] == "Admin":
                if len(admin_list) > 0:
                    admin_list.sort(key=lambda x: x['created_at'], reverse=False)
                    return {
                        'statusCode': 200,
                        'body': admin_list
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No test series are added yet"
                    }
            else:
                if len(tenant_list) > 0:
                    tenant_list.sort(key=lambda x: x['created_at'], reverse=False)
                    return {
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
                'body': 'Token is Invalid please re-login'
            }

    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
