from kafka import KafkaConsumer
from json import loads

tenant_id = "tenant_1"  # Replace with the actual tenant ID
topic_name = f"medicine_{tenant_id}"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode("utf-8")),
)

for message in consumer:
    print(f"Received message: {message.value}")