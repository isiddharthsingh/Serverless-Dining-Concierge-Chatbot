from datetime import datetime
import boto3
from decimal import Decimal

# Replace with your Yelp API key
YELP_API_KEY = 'your yelp API key'

# Replace with your AWS credentials and region
AWS_ACCESS_KEY = 'yourawsaccesskey'
AWS_SECRET_KEY = 'yourawssecretkey'
AWS_REGION = 'us-east-1'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

# Define the table name and partition key
table_name = 'yelp-restaurants'
partition_key = 'BusinessID'

# Check if the table already exists
existing_tables = dynamodb.tables.all()
table_exists = any(table.name == table_name for table in existing_tables)

# Create the table if it doesn't exist
if not table_exists:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': partition_key,
                'KeyType': 'HASH'  # HASH indicates the partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': partition_key,
                'AttributeType': 'S'  # S indicates String; use appropriate type if different
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait for the table to be created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

# Use the created table
table = dynamodb.Table(table_name)

# Function to query Yelp API
def get_yelp_data(term, location, limit=50, offset=0):
    headers = {'Authorization': f'Bearer {YELP_API_KEY}'}
    params = {'term': term, 'location': location, 'limit': limit, 'offset': offset}

    response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
    return json.loads(response.text)

# Function to insert data into DynamoDB
def insert_into_dynamodb(data):
    timestamp = datetime.utcnow().isoformat()

    for key, value in data.items():
        if isinstance(value, (float, int)):
            data[key] = Decimal(str(value))
        elif isinstance(value, dict):
            # Recursively convert nested dictionaries
            data[key] = {k: Decimal(str(v)) if isinstance(v, (float, int)) else v for k, v in value.items()}

    # Ensure only numeric values in the data dictionary are converted to Decimal
    data = {key: Decimal(str(value)) if isinstance(value, (float, int)) else value for key, value in data.items()}

    data['insertedAtTimestamp'] = timestamp
    table.put_item(Item=data)

# Search and insert data into DynamoDB
cuisine_types = ['Chinese', 'Italian', 'Indian']
total_items_per_cuisine = 50

for cuisine in cuisine_types:
    offset = 0
    count = 0

    while count < total_items_per_cuisine:
        result = get_yelp_data(term=f'{cuisine} restaurants', location='Manhattan, NY', limit=50, offset=offset)
        businesses = result.get('businesses', [])

        if not businesses:
            break

        for business in businesses:
            business_id = business['id']

            # Check if the business already exists in DynamoDB
            if not table.get_item(Key={partition_key: business_id}).get('Item'):
                insert_into_dynamodb({
                    partition_key: business_id,
                    'Name': business['name'],
                    'Address': business['location']['address1'],
                    'Coordinates': business['coordinates'],
                    'Number_of_Reviews': business['review_count'],
                    'Rating': business['rating'],
                    'Zip_Code': business['location']['zip_code'],
                    'Cuisine': cuisine
                })

                count += 1

        offset += 50

print("Data uploaded to DynamoDB successfully!")
