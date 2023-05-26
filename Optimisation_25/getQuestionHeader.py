import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
question_table = dynamodb.Table('Question')
token_data_table = dynamodb.Table('Token')

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
        return False

def lambda_handler(event, context):
    """
    Lambda function entry point.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Lambda function context.

    Returns:
        dict: Response containing the status code and body.
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
        
        if token_checker(event['token']):
            response = question_table.scan()
            result = response['Items']
            
            while 'LastEvaluatedKey' in response:
                response = question_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            
            tenant_list = []
            admin_list = []
            
            if 'email' not in event:
                event['email'] = ""
                event['role'] = ""
            
            for i in result:
                if event['email'] == i['Tenantemail']:
                    question_dict = {}
                    question_dict['id'] = i['id']
                    question_dict['topic'] = i['topic']
                    question_dict['description'] = i['description']
                    question_dict['series_title'] = i['series_title']
                    question_dict['Tenantemail'] = i['Tenantemail']
                    question_dict['name'] = i['name']
                    question_dict['status'] = i['status']
                    question_dict['created_at'] = i['created_at']
                    tenant_list.append(question_dict)
                
                if event['role'] == "Admin":
                    question_dict = {}
                    question_dict['id'] = i['id']
                    question_dict['topic'] = i['topic']
                    question_dict['description'] = i['description']
                    question_dict['series_title'] = i['series_title']
                    question_dict['Tenantemail'] = i['Tenantemail']
                    question_dict['name'] = i['name']
                    question_dict['status'] = i['status']
                    question_dict['created_at'] = i['created_at']
                    admin_list.append(question_dict)
            
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
                'body': 'Token is invalid, please re-login'
            }
        
    except (TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
