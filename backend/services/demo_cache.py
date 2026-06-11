from __future__ import annotations

import time
from typing import Any
from backend.core.config import settings

class DemoCache:
    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.DEMO_CACHE_TTL_SECONDS
        self.cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> tuple[Any, float] | None:
        if key not in self.cache:
            return None
        timestamp, value = self.cache[key]
        age = time.time() - timestamp
        if age > self.ttl_seconds:
            del self.cache[key]
            return None
        return value, age

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = (time.time(), value)

    def clear(self) -> None:
        self.cache.clear()
