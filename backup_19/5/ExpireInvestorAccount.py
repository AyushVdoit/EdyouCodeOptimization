import json
import boto3
dynamodb = boto3.resource('dynamodb')
Investor=dynamodb.Table('Investor')
Token_Data = dynamodb.Table('Token')
def TokenChecker(token):
    Data=Token_Data.get_item(Key={'token' : token})
    if 'Item' in Data:
        return True
    else:
        Data=Token_Data_Prod.get_item(Key={'token' : token})
        if 'Item' in Data:
            return True
        else:
            return False 

def lambda_handler(event, context):
    if TokenChecker(event['token']):
    # TODO implement
        # Data=Investor.get_item(Key={'email' : event['email'].lower()})
        # if 'Item' in Data:
        #     return{
        #         'statusCode':200,
        #         'body':Data['Item']
                
        #     }
        Investor.update_item(
            Key={
                    'email' : event['email'].lower(),
                },
        UpdateExpression="set expiredPassword = :g, expire_time =:h",
        ExpressionAttributeValues={
                ':g': True,
                ':h':0
            },
        ReturnValues="UPDATED_NEW"
        )
        return{
                'statusCode':200,
                "body":"Account Expired"
            }
    else:
        return {
            'statusCode': 401,
            'body': 'Token is Invalid please re-login'
        }
