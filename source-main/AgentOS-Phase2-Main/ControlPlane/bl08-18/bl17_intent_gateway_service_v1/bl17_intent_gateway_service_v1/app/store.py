# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from typing import Dict, List, Optional

from .models import IntentDraft

class InMemoryIntentStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._items: Dict[str, IntentDraft] = {}

    def upsert(self, item: IntentDraft) -> IntentDraft:
        with self._lock:
            self._items[item.intent_id] = item
            return item

    def get(self, intent_id: str) -> Optional[IntentDraft]:
        with self._lock:
            return self._items.get(intent_id)

    def list(self) -> List[IntentDraft]:
        with self._lock:
            items = list(self._items.values())
        items.sort(key=lambda x: x.created_at_utc, reverse=True)
        return items
