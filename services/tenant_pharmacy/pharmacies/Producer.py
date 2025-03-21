from time import sleep
from kafka import KafkaProducer
from json import dumps
import socket

class ProducerUserCreated:
    def __init__(self, tenant_id) -> None:
        self.topic_name = f'user_{tenant_id}'
        conf = {
            "bootstrap.servers": "localhost:9092",
            "client.id": socket.gethostname(),
        }
        self.producer = KafkaProducer(**conf)

    def publish(self, method, body):
        print(f"Inside UserService: Sending to Kafka for tenant {self.topic_name}: ")
        print(body)
        self.producer.send(
            topic=self.topic_name,
            key=b"key.user.created",
            value=dumps(body).encode('utf-8'),
        )
