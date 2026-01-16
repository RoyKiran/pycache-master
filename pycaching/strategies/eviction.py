"""Eviction policy implementations (LRU, LFU, FIFO)."""

from typing import Deque, Dict, Optional
from collections import OrderedDict, deque
from threading import Lock

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class LRUEvictionStrategy(BaseStrategy):
    """
    Least Recently Used (LRU) eviction strategy.

    Evicts the least recently used items when the cache is full.
    """

    def __init__(self, max_size: int = 100, name: str = "lru"):
        super().__init__(name)
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._access_order: OrderedDict[CacheKey, None] = OrderedDict()
        self._lock = Lock()

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, updating access order."""
        value = backend.get(key)
        if value is not None:
            with self._lock:
                # Move to end (most recently used)
                if key in self._access_order:
                    self._access_order.move_to_end(key)
                else:
                    self._access_order[key] = None
        elif miss_callback is not None:
            value = miss_callback(key)
            if value is not None:
                self.set(backend, key, value)
        return value

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value, evicting if necessary."""
        with self._lock:
            # Check if we need to evict
            if key not in self._access_order and len(self._access_order) >= self.max_size:
                # Evict least recently used
                lru_key = next(iter(self._access_order))
                backend.delete(lru_key)
                del self._access_order[lru_key]

            # Add/update in access order
            self._access_order[key] = None
            self._access_order.move_to_end(key)

        return backend.set(key, value, ttl)

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a key and remove from access order."""
        result = backend.delete(key)
        if result:
            with self._lock:
                self._access_order.pop(key, None)
        return result

    def clear(self, backend: Backend) -> bool:
        """Clear cache and access order."""
        with self._lock:
            self._access_order.clear()
        return backend.clear()


class LFUEvictionStrategy(BaseStrategy):
    """
    Least Frequently Used (LFU) eviction strategy.

    Evicts the least frequently used items when the cache is full.
    """

    def __init__(self, max_size: int = 100, name: str = "lfu"):
        super().__init__(name)
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._access_counts: Dict[CacheKey, int] = {}
        self._lock = Lock()

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, incrementing access count."""
        value = backend.get(key)
        if value is not None:
            with self._lock:
                self._access_counts[key] = self._access_counts.get(key, 0) + 1
        elif miss_callback is not None:
            value = miss_callback(key)
            if value is not None:
                self.set(backend, key, value)
        return value

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value, evicting if necessary."""
        with self._lock:
            # Check if we need to evict
            if key not in self._access_counts and len(self._access_counts) >= self.max_size:
                # Evict least frequently used
                lfu_key = min(self._access_counts.items(), key=lambda x: x[1])[0]
                backend.delete(lfu_key)
                del self._access_counts[lfu_key]

            # Initialize access count if new key
            if key not in self._access_counts:
                self._access_counts[key] = 0

        return backend.set(key, value, ttl)

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a key and remove from access counts."""
        result = backend.delete(key)
        if result:
            with self._lock:
                self._access_counts.pop(key, None)
        return result

    def clear(self, backend: Backend) -> bool:
        """Clear cache and access counts."""
        with self._lock:
            self._access_counts.clear()
        return backend.clear()


class FIFOEvictionStrategy(BaseStrategy):
    """
    First In First Out (FIFO) eviction strategy.

    Evicts the oldest items when the cache is full.
    """

    def __init__(self, max_size: int = 100, name: str = "fifo"):
        super().__init__(name)
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._insertion_order: Deque[CacheKey] = deque()
        self._lock = Lock()

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value (doesn't affect insertion order)."""
        value = backend.get(key)
        if value is None and miss_callback is not None:
            value = miss_callback(key)
            if value is not None:
                self.set(backend, key, value)
        return value

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value, evicting if necessary."""
        with self._lock:
            # Check if we need to evict
            if key not in self._insertion_order and len(self._insertion_order) >= self.max_size:
                # Evict oldest (first in)
                oldest_key = self._insertion_order.popleft()
                backend.delete(oldest_key)

            # Add to insertion order if new
            if key not in self._insertion_order:
                self._insertion_order.append(key)

        return backend.set(key, value, ttl)

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a key and remove from insertion order."""
        result = backend.delete(key)
        if result:
            with self._lock:
                try:
                    self._insertion_order.remove(key)
                except ValueError:
                    pass  # Key not in queue
        return result

    def clear(self, backend: Backend) -> bool:
        """Clear cache and insertion order."""
        with self._lock:
            self._insertion_order.clear()
        return backend.clear()
