import json  # Library for working with JSON data
import boto3  # AWS SDK for Python
from uuid import uuid4  # Library for generating UUIDs
import base64  # Library for working with base64-encoded data

s3 = boto3.client('s3')  # Amazon S3 client for working with S3 buckets
dynamodb = boto3.resource('dynamodb')  # Amazon DynamoDB resource for working with DynamoDB tables
topic_table = dynamodb.Table('Topic')  # DynamoDB table for storing topic data
token_table = dynamodb.Table('Token')  # DynamoDB table for storing token data


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
        required_fields = ["Topic_id", "token", "qid", "correctAnswer", "Potential_Question"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': f'Error: {field} is required and cannot be empty'
                }
        
        if token_checker(event['token']):
            topic_data = topic_table.get_item(Key={'Topic_id': event["Topic_id"]})
            
            if 'Item' in topic_data:
                topic_dictionary = topic_data['Item']
                topic_list = topic_dictionary['question']
                topic = {}
                
                for question in event["Potential_Question"]:
                    if question['subQ'] is None or question['subQ'].strip() == '':
                        return {
                            'statusCode': 400,
                            'body': 'Question variations are required and cannot be empty'
                        }
                
                bucket_name = "pollydemo2022"
                object_key = 'images_dev/' + event['qid'] + '.jpg'
                
                if event['imageUrl'] != "":
                    content_type = 'image/jpeg'
                    if "https://pollydemo2022.s3.us-west-2.amazonaws.com/" in event['imageUrl']:
                        event['image'] = event['imageUrl']
                    else:
                        image = event['imageUrl'].replace("data:image/png;base64,", "")
                        image = base64.b64decode(image)
                        s3.put_object(Bucket=bucket_name, Key=object_key, Body=image, ContentType=content_type)
                        event['image'] = "https://pollydemo2022.s3.us-west-2.amazonaws.com/" + object_key
                    topic['image'] = event['image']
                    topic['imageUrl'] = event['image']
                else:
                    topic['image'] = ""
                    topic['imageUrl'] = ""
                
                if event['url'] != "" and event['url'] != None:
                    topic['url'] = event['url']
                else:
                    topic['url'] = ""
                
                if event['description'] != "" and event['description'] != None:
                    if event['prompt_status'] == True or event['prompt_status'] != None:
                        topic['description'] = event['description']
                    else:
                        topic['description'] = ""
                        event['prompt_status'] = False
                else:
                    topic['description'] = ""
                
                if event['url'] != "" and event['url'] != None:
                    topic['url'] = event['url']
                    
                    if event['followup'] != "" and event['followup'] != None:
                        if event['followup_status']:
                            topic['followup'] = event['followup']
                        else:
                            topic['followup'] = "click me"
                    else:
                        topic['followup'] = "click me"
                else:
                    topic['url'] = ""
                    topic['followup'] = ""
                
                topic['correctAnswer'] = (
                    event['correctAnswer']
                    + "7481903939urlforyou="
                    + topic['url']
                    + "7581903939imagelinkforyou="
                    + topic['image']
                    + "7581904949Textlinkforyou="
                    + topic['description']
                    + "7581904949Followup="
                    + topic['followup']
                )
                
                topic['Potential_Question'] = event['Potential_Question']
                topic['qid'] = event['qid']
                topic['prompt_status'] = event['prompt_status']
                topic['followup_status'] = event['followup_status']
                
                index = next((i for i, q in enumerate(topic_list) if q['qid'] == event['qid']), None)
                
                if index is not None:
                    topic_list[index] = topic
                    topic_dictionary['question'] = topic_list
                    topic_table.put_item(Item=topic_dictionary)
                    return {
                        'statusCode': 200,
                        'body': "Question updated successfully"
                    }
                else:
                    return {
                        'statusCode': 200,
                        'body': 'No item Found'
                    }
                
            else:
                return {
                    'statusCode': 200,
                    'body': 'No item Found'
                }
        else:
            return {
                'statusCode': 401,
                'body': 'Token is Invalid please re-login'
            }
        
    except (
        TypeError, ValueError, IndexError, LookupError, SyntaxError, NameError, json.JSONDecodeError, SyntaxError
    ) as e:
        return {
            'statusCode': 400,
            'body': f'Error: {e}'
        }
