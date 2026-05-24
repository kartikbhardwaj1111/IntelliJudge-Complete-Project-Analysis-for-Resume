"""
Thread-safe in-memory rate limiter using a sliding window.

WHY threading.Lock instead of asyncio.Lock:
  AI service calls run inside asyncio.to_thread() which spawns real OS threads.
  asyncio primitives are NOT thread-safe across threads; threading.Lock is.
"""

import threading
import time
from collections import defaultdict, deque

from app.utils.exceptions import AppException


class _RateLimiter:
    def __init__(self, max_calls: int = 5, window_seconds: int = 60) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._buckets: dict = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, user_id: str, endpoint: str) -> None:
        """Raise 429 if the user has exceeded the limit. Thread-safe."""
        key = f"{user_id}:{endpoint}"
        now = time.monotonic()
        cutoff = now - self._window

        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self._max:
                raise AppException(
                    status_code=429,
                    message=(
                        f"Rate limit exceeded. You may make {self._max} AI "
                        "requests per minute. Please wait and try again."
                    ),
                )
            bucket.append(now)


# Singleton — shared across all requests
ai_rate_limiter = _RateLimiter(max_calls=5, window_seconds=60)
