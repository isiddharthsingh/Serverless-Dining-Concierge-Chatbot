import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import random
import requests

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string
        return super(DecimalEncoder, self).default(obj)
        
def convert_to_valid_json(json_with_single_quotes):
    # Replace single quotes with double quotes
    json_with_double_quotes = json_with_single_quotes.replace("'", '"')
    return json_with_double_quotes
    
def lambda_handler(event, context):
    print("event lol")
    print(event)
    # Initialize the SQS client
    sqs = boto3.client('sqs')
    dynamodb = boto3.client('dynamodb')
    sesClient = boto3.client('ses',region_name='us-east-1')
    # Specify the SQS queue URL,
    queue_url = 'https://sqs.us-east-1.amazonaws.com/685928798852/restraunt_request'  # Replace with your SQS queue URL
    # Process each record in the event
    print(event)
    print("lolx ")
    for record in event['Records']:
        # Extract the message body
        print(record)
        message_body = json.loads(convert_to_valid_json(record["body"]))
        # Print the message to the CloudWatch logs (replace with your processing logic)
        print(f"Received message: {message_body}")
        # Perform your custom processing here
        # Delete the processed message from the queue
        receipt_handle = record['receiptHandle']
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    

    # Define the DynamoDB table name
    es_endpoint = "https://search-restaurantsdomain-tugn4e7mdcoa6cbfdjnzdqthvu.us-east-1.es.amazonaws.com"
    es_index = "restaurant"
    table_name = "yelp-restaurants"
    input_cuisine = message_body["Cuisine"]["StringValue"]
    print("lol0")
    print(input_cuisine)
    es_username = "root"
    es_password = "Root@123"
    region = "us-east-1"
    search_query = {"query":{"bool":{"must":[{"match":{"cuisine":input_cuisine}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
    # Define the Elasticsearch search query
    search_url = f"{es_endpoint}/{es_index}/_search"
    try:
        # Perform the Elasticsearch search using HTTP POST
        response = requests.post(search_url, json=search_query,auth=(es_username, es_password))
        if response.status_code == 200:
            data = response.json()
            print("lol1")
            print(data)
            restaurant_hits = data['hits']['hits']
            print(restaurant_hits)
            print("lol2")
            # Extract RestaurantId values from the search results
            restaurant_ids = [hit['_source']['restaurantid'] for hit in restaurant_hits]
            # Shuffle the results to make them appear random
            print("restaurant  ids ")
            print(restaurant_ids)
            random.shuffle(restaurant_ids)
            # Return the first 3 randomized RestaurantId values
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error making Elasticsearch request"})
        }
    try:
        # Creating the DynamoDB Client
        dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
        # Creating the DynamoDB Table Resource
        dynamodb2 = boto3.resource('dynamodb', region_name="us-east-1")
        table = dynamodb2.Table(table_name)
        print("lol dyna 1")
        response0 = table.query(
            KeyConditionExpression=Key('BusinessID').eq(restaurant_ids[0])
        )
        print("lol dyna 2")
        response1 = table.query(
            KeyConditionExpression=Key('BusinessID').eq(restaurant_ids[1])
        )
        print("lol dyna 3")
        response2 = table.query(
            KeyConditionExpression=Key('BusinessID').eq(restaurant_ids[2])
        )
        print("lol dyna 4")
        print(response0)
        print(response1)
        print(response2)
        item0 = response0.get('Items', {})
        item1 = response1.get('Items', {})
        item2 = response2.get('Items', {})
        print(item0)
       
        print("lolol1")
        print(item1[0]["Name"])
        print(item2[0]["Name"])
        print(item0[0]["Address"])
        print("deets")
        print(message_body["Email"]["StringValue"])
        print(message_body["Date"]["StringValue"])
        print(message_body["NumberOfPeople"]["StringValue"])
        print(message_body["Cuisine"]["StringValue"])
        print("lolol deets")
        
        

        destination = {'ToAddresses': [message_body["Email"]["StringValue"]]}
        print("sending email")
        print(destination)
        print("lolol")
        responseBody = """Hello! Here are my %s restaurant suggestions for %s people at %s:
1. %s, located at %s
2. %s, located at %s
3. %s, located at %s.
Enjoy your meal!""" % (message_body["Cuisine"]["StringValue"],
        message_body["NumberOfPeople"]["StringValue"],
        message_body["Date"]["StringValue"],
        item0[0]["Name"],item0[0]["Address"],
        item1[0]["Name"],item1[0]["Address"],
        item2[0]["Name"],item2[0]["Address"])
 
 
        print(responseBody)
        sesClient.send_email(
            Destination=destination,
            Message={
                'Body': {'Text': {'Data': responseBody}},
                'Subject': {'Data': 'Cuisine Recommendation'}
            },
            Source='singhsiddhart24@gmail.com'
        )
        print("sent mail")
        # Return the item as a JSON response
        return {
            'statusCode': 200,
            'body': json.dumps(item1,cls=DecimalEncoder)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': str(e)
        }