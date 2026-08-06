# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from typing import Dict, List, Optional

from .models import SuggestionEnvelope

class InMemorySuggestionStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._items: Dict[str, SuggestionEnvelope] = {}

    def upsert(self, env: SuggestionEnvelope) -> SuggestionEnvelope:
        with self._lock:
            self._items[env.suggestion_id] = env
            return env

    def get(self, suggestion_id: str) -> Optional[SuggestionEnvelope]:
        with self._lock:
            return self._items.get(suggestion_id)

    def list(self, status: Optional[str] = None) -> List[SuggestionEnvelope]:
        with self._lock:
            items = list(self._items.values())
        if status:
            items = [x for x in items if x.status == status]
        items.sort(key=lambda x: x.created_at_utc, reverse=True)
        return items
