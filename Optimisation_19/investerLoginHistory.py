import json
import boto3
from boto3.dynamodb.conditions import Key
from time import gmtime, strftime

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define DynamoDB tables
# Table for investor login history
investor = dynamodb.Table('InvestorLoginHistory')
token_data = dynamodb.Table('Token')  # Table for token data
# Table for production token data
token_data_prod = dynamodb.Table('Token_Prod')


def token_checker(token):
    """
    Checks if the token is valid by searching for it in the token data tables.

    Args:
        token (str): The token to be checked.

    Returns:
        bool: True if the token is found in any of the tables, False otherwise.
    """
    data = token_data.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        data = token_data_prod.get_item(Key={'token': token})
        if 'Item' in data:
            return True
        else:
            return False


def lambda_handler(event, context):
    if token_checker(event['token']):
        now = strftime("%Y-%m-%d,%H:%M:%S", gmtime())
        now1 = "2023-02-02,00:00:00"

        # Query the investor login history table for records matching the email and time range
        resp = investor.query(
            KeyConditionExpression=Key('email').eq(
                event['email']) & Key('time').between(now1, now),
            ScanIndexForward=False
        )

        result = []
        for i in resp['Items']:
            conversation = "not started"
            if len(i['data']) != 0:
                conversation = "started"

            # Prepare the data item for the response
            data_item = {
                'email': i['email'],
                'time': i['time'],
                'conversation': conversation,
                "logout": i['logout'],
                "Session": i['Session'],
                "Ip_Address": i['Ip_Address']
            }
            result.append(data_item)

        return {
            'statusCode': 200,
            'body': result
        }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is invalid. Please re-login'
        }
