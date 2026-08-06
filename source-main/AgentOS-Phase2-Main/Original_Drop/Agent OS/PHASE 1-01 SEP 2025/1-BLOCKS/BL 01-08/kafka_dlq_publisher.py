from confluent_kafka import Producer
import json

class DLQPublisher:
    def __init__(self, brokers, topic):
        self.producer = Producer({"bootstrap.servers": brokers})
        self.topic = topic

    def publish(self, event: dict):
        self.producer.produce(self.topic, json.dumps(event).encode("utf-8"))
        self.producer.flush()
