import json
import boto3

# Initialize SQS client
sqs = boto3.client('sqs')

# SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/685928798852/restraunt_request'

def lambda_handler(event, context):
    print(":hello")
    print("event")
    print("hello")
    intent_name = event['currentIntent']['name']

    # Initialize response
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
        }
    }

    # Handle GreetingIntent
    if intent_name == "GreetingIntent":
        response["dialogAction"]["message"] = {
            "contentType": "PlainText",
            "content": "Hi there, how can I help?"
        }

    # Handle ThankYouIntent
    elif intent_name == "ThankYouIntent":
        response["dialogAction"]["message"] = {
            "contentType": "PlainText",
            "content": "You're welcome! If you have any more questions, feel free to ask."
        }

    # Handle DiningSuggestionsIntent
    elif intent_name == "DiningSuggestionsIntent":
        print("lol")
        slots = event['currentIntent']['slots']
       
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
       
    else:
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed",
                "message": {
                    "contentType": "PlainText",
                    "content": "Sorry, I didn't understand that request."
                }
            }
        }
    print("over")


    return response