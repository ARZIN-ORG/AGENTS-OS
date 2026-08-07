"""Minimal compiler: reads agent .md definitions and creates Kafka topics."""
import os
import json
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

KAFKA_BROKER = "localhost:9092"
AGENT_DIR = ".claude/agents"

def load_agent_names(directory: str):
    names = []
    if not os.path.isdir(directory):
        print(f"Agent directory '{directory}' not found, skipping agent-specific topics.")
        return names
    for f in os.listdir(directory):
        if f.endswith(".md"):
            agent_name = os.path.splitext(f)[0]
            names.append(agent_name)
    return names

def create_topics(agent_names):
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER, client_id="agent-compiler")
    # Essential topics
    topics = [
        "claude-agent-recommendations",
        "governance-decisions",
        "agent-commands",
        "agent-events",
    ]
    # Per-agent input topics
    for name in agent_names:
        topics.append(f"agent-{name}-inputs")
        topics.append(f"agent-{name}-outputs")

    topic_objects = [NewTopic(name=t, num_partitions=1, replication_factor=1) for t in topics]
    for topic_obj in topic_objects:
        try:
            admin.create_topics([topic_obj])
            print(f"Created topic: {topic_obj.name}")
        except TopicAlreadyExistsError:
            print(f"Topic already exists: {topic_obj.name}")
    admin.close()
    print("Compiler finished.")

if __name__ == "__main__":
    agents = load_agent_names(AGENT_DIR)
    create_topics(agents)
