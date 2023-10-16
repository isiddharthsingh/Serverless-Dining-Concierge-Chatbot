import json
import boto3
import re

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    print("event type:", type(event))
    print("event keys:", event.keys())
    print(event)
    
    
    try:
        input_messages = event['messages']
        print("Input messages:", input_messages)

        # Extracting client_request and user_id from the last message
        last_message = input_messages[-1]['unstructured']['text']
        match = re.match(r'[0-9a-zA-Z._:-]+', last_message)
        if match:
            user_id = match.group()
        else:
            raise ValueError("Invalid user_id format")

        client_request = input_messages[0]['unstructured']['text']
        print("Client message:", client_request)
        print("User id:", user_id)

        bot_response = client.post_text(
            botName='DiningBot',
            botAlias='lexbot',
            userId=user_id,
            inputText=client_request
        )

        bot_message = bot_response['message'].strip()
        print("Bot response:", bot_message)
        
        output = ({"type":"unstructured","unstructured": {"text": bot_message}})
        temp = {'messages':[output]}

        return {
            "statusCode": 200,
            "data": temp,
            'Access-Control-Allow-Headers': 'Content-Type, Origin, X-Auth-Token',
            'Access-Control-Allow-Origin': '*'
        }
    except Exception as e:
        print(f"Error processing Lex request: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error processing Lex request: {e}"})
        }
