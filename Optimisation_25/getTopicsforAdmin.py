import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the required DynamoDB tables
topic_table = dynamodb.Table('Topic')
user_table = dynamodb.Table('user')
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
            response = topic_table.scan()
            result = response['Items']
            
            while 'LastEvaluatedKey' in response:
                response = topic_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])
            
            admin_list = []
            
            for i in result:
                if i['Tenantemail'] == "":
                    if i['Topic_id'] in ["433fff578ba64eb1a99fc10fdf98a9f8", "30abab44f3a140159fd4cb0b5f5d272f"]:
                        pass
                    else:
                        if i['status'] == "Active":
                            topic_dict = {}
                            topic_dict['Topic_id'] = i['Topic_id']
                            topic_dict['topicName'] = i['topicName']
                            topic_dict['description'] = i['description']
                            topic_dict['industry'] = i['industry']
                            topic_dict['status'] = i['status']
                            topic_dict['Tenantemail'] = i['Tenantemail']
                            topic_dict['name'] = i['name']
                            topic_dict['created_at'] = i['created_at']
                            admin_list.append(topic_dict)
            
            if len(admin_list) > 0:
                admin_list.sort(key=lambda x: x['created_at'], reverse=False)
                return {
                    'statusCode': 200,
                    'body': admin_list
                }
            else:
                return {
                    'statusCode': 205,
                    'body': "No topics are added yet"
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is invalid, please re-login'
            }
        
    except (TypeError, ValueError, IndexError, KeyError, LookupError, SyntaxError, NameError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
