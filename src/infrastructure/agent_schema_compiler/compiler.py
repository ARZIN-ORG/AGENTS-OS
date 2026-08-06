# -*- coding: utf-8 -*-
"""
Agent Schema Compiler (نسخه عملیاتی)
ورودی: فایل‌های `.claude/agents/*.md`
خروجی: JSON Schema + ایجاد خودکار توپیک در کافکا (با استفاده از AdminClient)
"""

import os
import json
import re
import time
from pathlib import Path
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

AGENTS_PATH = Path(".claude/agents")
OUTPUT_SCHEMA_PATH = Path("src/infrastructure/generated_schemas")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

def parse_markdown_agent(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    name = file_path.stem
    mission_match = re.search(r"\*\*Mission:\*\* (.*?)(?:\n|$)", content)
    responsibilities = re.findall(r"- (.*?)(?:\n|$)", content)
    return {
        "agent_id": name,
        "mission": mission_match.group(1).strip() if mission_match else "",
        "responsibilities": [r.strip() for r in responsibilities if r.strip()],
        "schema_version": "v1.0"
    }

def generate_json_schema(agent_data: dict) -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "agent_id": {"type": "string", "const": agent_data["agent_id"]},
            "intent_type": {"type": "string", "enum": ["RECOMMENDATION", "EXECUTION", "AUDIT"]},
            "payload": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "required_approval": {"type": "boolean"}
                }
            }
        },
        "required": ["agent_id", "intent_type", "payload"]
    }

def create_kafka_topic(topic_name: str, partitions: int = 1, replication: int = 1):
    """توپیک را در کافکا ایجاد می‌کند (اگر وجود نداشته باشد)."""
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)
        topic_list = [NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication)]
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"✅ توپیک کافکا ایجاد شد: {topic_name}")
    except TopicAlreadyExistsError:
        print(f"ℹ️ توپیک کافکا از قبل وجود دارد: {topic_name}")
    except Exception as e:
        print(f"❌ خطا در ایجاد توپیک کافکا: {e}")

def compile_all():
    OUTPUT_SCHEMA_PATH.mkdir(parents=True, exist_ok=True)
    print("🔨 کامپایل خودکار ایجنت‌ها و ایجاد زیرساخت کافکا...")
    
    for md_file in AGENTS_PATH.glob("*.md"):
        agent_data = parse_markdown_agent(md_file)
        schema = generate_json_schema(agent_data)
        
        output_file = OUTPUT_SCHEMA_PATH / f"{agent_data['agent_id']}_schema.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        
        kafka_topic = f"agent-{agent_data['agent_id']}-inputs"
        create_kafka_topic(kafka_topic)
        print(f"   📨 توپیک مرتبط: {kafka_topic}")

    print("✅ کامپایل و ایجاد توپیک‌ها کامل شد!")

if __name__ == "__main__":
    # یک تاخیر کوچک می‌گذاریم تا اطمینان حاصل شود که کافکا بالا آمده است
    time.sleep(5)
    compile_all()
