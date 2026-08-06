# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict

class AacpPublisher:
    def __init__(self) -> None:
        self.topic = os.getenv("AACP_EXEC_REQUEST_TOPIC", "aacp.exec.request")
        self._impl = None
        try:
            from aacp_kafka_manager_PLUG_WIRED_BL08_v1 import AacpKafkaManager  # type: ignore
            self._impl = AacpKafkaManager()
        except Exception:
            self._impl = None

    def publish_exec_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if self._impl is None:
            return {"published": False, "mode": "noop", "topic": self.topic}
        self._impl.publish(self.topic, message)
        return {"published": True, "mode": "kafka_manager", "topic": self.topic}
