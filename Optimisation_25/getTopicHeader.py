import json  # Library for working with JSON data
import boto3  # AWS SDK library for Python
from boto3.dynamodb.conditions import Key  # Condition expression helper for DynamoDB queries

# Initializing the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Accessing the 'Topic' table in DynamoDB
topic_table = dynamodb.Table('Topic')

# Accessing the 'user' table in DynamoDB
user_table = dynamodb.Table('user')

# Accessing the 'Token' table in DynamoDB
token_table = dynamodb.Table('Token')

# Function to check the validity of a token in the Token table
def token_checker(token):
    """
    Checks the validity of a token in the Token table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False  

# AWS Lambda function handler
def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Args:
        event (dict): Event data passed to the Lambda function.
        context (object): Context object representing the runtime information.

    Returns:
        dict: Response data to be returned by the Lambda function.
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
            # TODO implement
            response = topic_table.scan()
            result = response['Items']
            while 'LastEvaluatedKey' in response:
                response = topic_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            
            tenant_list = []
            admin_list = []
            
            if 'email' not in event:
                event['email'] = ""
                event['role'] = ""
            
            for i in result:
                if event['email'] == i['Tenantemail']:
                    topic_dict = {}
                    topic_dict['Topic_id'] = i["Topic_id"]
                    topic_dict["topicName"] = i["topicName"]
                    topic_dict['description'] = i['description']
                    topic_dict['industry'] = i["industry"]
                    topic_dict['status'] = i["status"]
                    topic_dict['Tenantemail'] = i['Tenantemail']
                    topic_dict['name'] = i['name']
                    topic_dict['created_at'] = i['created_at']
                    tenant_list.append(topic_dict)
                
                if event['role'] == "Admin":
                    if i['Topic_id'] in ["433fff578ba64eb1a99fc10fdf98a9f8", "30abab44f3a140159fd4cb0b5f5d272f"]:
                        pass
                    else:
                        topic_dict = {}
                        topic_dict['Topic_id'] = i["Topic_id"]
                        topic_dict["topicName"] = i["topicName"]
                        topic_dict['description'] = i['description']
                        topic_dict['industry'] = i["industry"]
                        topic_dict['status'] = i["status"]
                        topic_dict['Tenantemail'] = i['Tenantemail']
                        topic_dict['name'] = i['name']
                        topic_dict['created_at'] = i['created_at']
                        admin_list.append(topic_dict)
            
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
                        'body': "No Topics have been added yet"
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
                        'body': "No Topics have been added yet"
                    }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }
    except (TypeError, ValueError, IndexError, KeyError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
