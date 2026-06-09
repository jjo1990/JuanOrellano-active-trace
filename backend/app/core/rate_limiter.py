import asyncio
import time
from collections import defaultdict
from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiterProtocol(Protocol):
    async def check(self, key: str) -> bool:
        ...

    async def reset(self, key: str) -> None:
        ...


class InMemoryRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - self._window_seconds
        async with self._lock:
            timestamps = self._store[key]
            self._store[key] = [t for t in timestamps if t > window_start]
            if len(self._store[key]) >= self._max_attempts:
                return False
            self._store[key].append(now)
            return True

    async def reset(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)
