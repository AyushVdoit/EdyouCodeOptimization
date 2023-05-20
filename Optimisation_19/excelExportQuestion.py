import json
import boto3
from uuid import uuid4
import secrets
from boto3.dynamodb.conditions import Key

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get the Question and Token tables
question_table = dynamodb.Table('Question')
token_table = dynamodb.Table('Token')


def token_checker(token):

    data = token_table.get_item(Key={'token': token})
    if 'Item' in data:
        return True
    else:
        return False


def lambda_handler(event, context):

    # Check token validity
    if token_checker(event['token']):
        data = event['data']
        data_copy = data
        missing_fields_message = "The fields are missing at column "
        missing_fields = []
        count = 1

        for data_item in data_copy:
            count += 1
            required_fields = ["correctAnswer", "description__001", "description__002", "description__003", "description__004",
                               "description__005", "options__001", "options__002", "options__003", "options__004", "options__005", "Question", "hint"]
            field_letters = {'correctAnswer': 'A', 'description__001': 'B', 'description__002': 'C', 'description__003': 'D', 'description__004': 'E',
                             'description__005': 'F', 'options__001': 'G', 'options__002': 'H', 'options__003': 'I', 'options__004': 'J', 'options__005': 'K', 'Question': 'L', 'hint': 'M'}

            for field in required_fields:
                if field not in data_item or not data_item[field]:
                    missing_fields.append(field_letters[field] + str(count))

        if len(missing_fields) > 0:
            missing_fields_string = ', '.join(missing_fields)
            return {
                'statusCode': 400,
                'body': missing_fields_message + missing_fields_string
            }

        question_data = question_table.get_item(Key={'id': event['id']})

        if 'Item' in question_data:
            question_dict = question_data['Item']
            question_list = question_dict['question']

            for data_item in data:
                descriptions = []
                options = []

                # Extract descriptions and options from the input data
                for key in data_item:
                    if key.startswith("description__"):
                        descriptions.append(data_item[key])
                    elif key.startswith("options__"):
                        options.append(data_item[key])

                question = {}

                option_letters = ["A.", "B.", "C.", "D.", "E."]
                new_options = []

                # Construct options with letters (e.g., A. Option 1)
                for i, option in enumerate(options):
                    new_option = f"{option_letters[i]} {option}"
                    new_options.append(new_option)

                lowercase_options = [o.lower() for o in options]
                correct_option_index = lowercase_options.index(
                    data_item['correctAnswer'].lower())
                replacements = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
                new_value = {0: "Option A", 1: "Option B",
                             2: "Option C", 3: "Option D", 4: "Option E"}

                question['correctAnswer'] = option_letters[correct_option_index] + \
                    " " + options[correct_option_index]
                question['correctPosition'] = correct_option_index
                question["options"] = new_options

                if 'hint' in data_item:
                    question['hint'] = data_item['hint']
                else:
                    question['hint'] = ""

                for i, desc in enumerate(descriptions):
                    if i == correct_option_index:
                        descriptions[i] = replacements[i] + \
                            " is correct because " + descriptions[i]
                    else:
                        descriptions[i] = replacements[i] + \
                            " is incorrect because " + descriptions[i]

                question['description'] = descriptions
                question['correctAnswerFrontend'] = new_value[correct_option_index]

                question["Question"] = data_item['Question']
                question['qid'] = uuid4().hex
                question_list.append(question)

            question_dict['question'] = question_list
            question_table.put_item(Item=question_dict)

            return {
                'statusCode': 200,
                'body': "File Uploaded Successfully"
            }
