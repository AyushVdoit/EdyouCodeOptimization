import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
investor_table = dynamodb.Table('Investor')
token_data_table = dynamodb.Table('Token')
token_data_prod_table = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Check if the provided token is valid.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_data_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        data = token_data_prod_table.get_item(Key={'token': token})
        if 'Item' in data:
            return True
        else:
            return False


def lambda_handler(event, context):
    try:
        data = event
        required_fields = ["token"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        if token_checker(event['token']):
            response = investor_table.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = investor_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            tenant_list = []
            admin_list = []
            if 'email' not in event:
                event['email'] = ""
                event['role'] = ""
            for i in result:
                if event['email'] == i['tenantEmail']:
                    tenant_list.append(i)
                if event['role'] == "Admin":
                    admin_list.append(i)
            if event['role'] == "Admin":
                if len(admin_list) > 0:
                    admin_list.sort(key=lambda x: x['created_at'])
                    return {
                        'statusCode': 200,
                        'body': admin_list
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No Investor added yet"
                    }
            else:
                if len(tenant_list) > 0:
                    tenant_list.sort(key=lambda x: x['created_at'])
                    return {
                        'statusCode': 200,
                        'body': tenant_list
                    }
                else:
                    return {
                        'statusCode': 205,
                        'body': "No Investor added yet"
                    }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }
    except (
            TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError,
            SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
