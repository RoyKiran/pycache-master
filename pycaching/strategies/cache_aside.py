"""Cache-aside (lazy loading) strategy implementation."""

from typing import Optional

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class CacheAsideStrategy(BaseStrategy):
    """
    Cache-aside strategy (lazy loading).

    The application is responsible for loading data into the cache.
    On cache miss, the miss_callback is invoked to load the data.
    """

    def __init__(self, name: str = "cache_aside"):
        super().__init__(name)

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, loading from source on miss."""
        # Try to get from cache
        value = backend.get(key)

        # If miss and callback provided, load from source
        if value is None and miss_callback is not None:
            value = miss_callback(key)
            if value is not None:
                # Store in cache for future requests
                backend.set(key, value)
            return value

        return value

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        return backend.set(key, value, ttl)
