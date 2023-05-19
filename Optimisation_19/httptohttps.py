import json
import requests
import time


def lambda_handler(event, context):
    # TODO implement

    url = "http://ec2-34-216-218-31.us-west-2.compute.amazonaws.com"

    # Handle different values of 'data' field in the event
    if event['data'] == "init":
        url = url + "/demo"
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

    if event['data'] == "train":
        url = url + "/training"
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

    if event['data'] == "run":
        url = url + "/running"
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        time.sleep(2)

    print(response.text)

    return {
        'statusCode': 200
    }
