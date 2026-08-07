"""Minimal bridge: forwards recommendations to agent-specific topics."""
import json
import sys
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

KAFKA_BROKER = "localhost:9092"
SOURCE_TOPIC = "claude-agent-recommendations"

def main():
    print("Starting agent bridge...")
    try:
        consumer = KafkaConsumer(
            SOURCE_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest',
            group_id='agent-bridge',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )
    except KafkaError as e:
        print(f"Kafka error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Bridge running. Forwarding messages...")
    for message in consumer:
        rec = message.value
        agent_id = rec.get("agent_id", "unknown")
        target_topic = f"agent-{agent_id}-inputs"
        producer.send(target_topic, value=rec)
        producer.send("agent-commands", value=rec)   # also notify command channel
        print(f"Routed to {target_topic}: {rec.get('event_id', 'no-id')}")

if __name__ == "__main__":
    main()
