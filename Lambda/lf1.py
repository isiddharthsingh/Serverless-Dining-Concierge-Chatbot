import json
import boto3
import re

# Initialize SQS client
sqs = boto3.client('sqs')

# SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/685928798852/restraunt_request'

def handle_greeting_intent():
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "Hi there, how can I serve you?"
            }
        }
    }

def handle_thank_you_intent():
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "You're welcome! If you have any more questions, feel free to ask."
            }
        }
    }
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def validate_dining_request(slots):
    # Validate Location
    location = slots.get('Location')
    
    # location_types = ['manhattan', 'new york', 'ny', 'nyc']
    if not location:
        return "Please provide a valid location."

    # Validate Cuisine
    cuisine = slots.get('Cuisine')
    #  cuisine_types = ['Chinese', 'Indian', 'Italian', 'china', 'india', 'italy']
    # or cuisine.lower() not in cuisine_types
    if not cuisine  :
        return "Please specify the cocrrect cuisine."


    # Validate DiningTime
    dining_time = slots.get('Time')
    if not dining_time:
        return "Please provide a dining time."

    # Validate NumberOfPeople
    num_people = slots.get('NumberOfPeople')
    if not num_people or not num_people.isdigit():
        return "Please specify the number of people for the reservation. "

    # Validate Email (You can add a more sophisticated email validation)
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    email = slots.get('Email')
    if not email or not "@" in email or not re.match(pattern, email):
        return "Please provide a valid email address."

    return None  # No validation errors

def handle_dining_request(event):
    slots = event['currentIntent']['slots']

    # Validate the dining request
    validation_error = validate_dining_request(slots)
    if validation_error:
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed",
                "message": {
                    "contentType": "PlainText",
                    "content": validation_error
                }
            }
        }

    # Prepare the message
    message_attributes = {
        'Location': {'StringValue': slots['Location'], 'DataType': 'String'},
            'Cuisine': {'StringValue': slots['Cuisine'], 'DataType': 'String'},
            'Date': {'StringValue': slots['Date'], 'DataType': 'String'},
            'Time': {'StringValue': slots['Time'], 'DataType': 'String'},
            'NumberOfPeople': {'StringValue': str(slots['NumberOfPeople']), 'DataType': 'Number'},
            'Email': {'StringValue': slots['Email'], 'DataType': 'String'}
    }

    # Send message to SQS queue
    sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes=message_attributes,
        MessageBody=json.dumps(message_attributes)
    )

    # Respond to the user
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "We have received your request and will notify you via email with a list of restaurant suggestions."
            }
        }
    }

def lambda_handler(event, context):
    intent_name = event['currentIntent']['name']

    if intent_name == "GreetingIntent":
        return handle_greeting_intent()
    elif intent_name == "ThankYouIntent":
        return handle_thank_you_intent()
    elif intent_name == "DiningSuggestionsIntent":
        return handle_dining_request(event)
    else:
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed",
                "message": {
                    "contentType": "PlainText",
                    "content": "Sorry, I did not understand that request."
                }
            }
        }