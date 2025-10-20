import time
import json
import requests
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable, TopicAlreadyExistsError
from kafka.admin import NewTopic

API_KEY = ""
BASE_URL = "https://finnhub.io/api/v1/quote"
SYMBOLS = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
TOPIC_NAME = "Stock"  # Match your Kafka topic exactly (case-sensitive)

# Retry loop to connect to Kafka broker
producer = None
while not producer:
    try:
        producer = KafkaProducer(
            bootstrap_servers=["localhost:29092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks='all'
        )
        print("Connected to Kafka broker.")
    except NoBrokersAvailable:
        print("Kafka broker not ready, retrying in 5 seconds...")
        time.sleep(5)

# Optional: Create topic if it doesn't exist
try:
    admin_client = KafkaAdminClient(bootstrap_servers="localhost:29092")
    topic_list = [NewTopic(name=TOPIC_NAME, num_partitions=3, replication_factor=1)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    print(f"Topic '{TOPIC_NAME}' created successfully.")
except TopicAlreadyExistsError:
    print(f"Topic '{TOPIC_NAME}' already exists.")
except Exception as e:
    print(f"Error creating topic: {e}")

# Function to fetch stock quotes
def fetch_quote(symbol):
    url = f"{BASE_URL}?symbol={symbol}&token={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        data["symbol"] = symbol
        data["fetched_at"] = int(time.time())
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# Loop to produce data continuously
while True:
    for symbol in SYMBOLS:
        quote = fetch_quote(symbol)
        if quote:
            print(f"Producing: {quote}")
            producer.send(TOPIC_NAME, value=quote)
            producer.flush()
    time.sleep(6)
