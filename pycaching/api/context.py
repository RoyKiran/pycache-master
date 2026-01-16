"""Context manager API for caching."""

from typing import Any, Callable, Optional

from pycaching.api.factory import create_cache
from pycaching.core.config import CacheConfig
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class CacheContext:
    """Context manager for cache operations."""

    def __init__(
        self,
        key: CacheKey,
        backend: Optional[str] = None,
        strategy: Optional[str] = None,
        config: Optional[CacheConfig] = None,
        ttl: Optional[float] = None,
    ):
        """
        Initialize cache context.

        Args:
            key: Cache key
            backend: Backend name
            strategy: Strategy name
            config: Optional CacheConfig
            ttl: Optional time-to-live
        """
        self.key = key
        self.ttl = ttl
        self.cache = create_cache(
            backend=backend or "memory",
            strategy=strategy or "cache_aside",
            config=config,
        )
        self.value: Optional[CacheValue] = None

    def __enter__(self) -> "CacheContext":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.cache.close()

    def get(self) -> Optional[CacheValue]:
        """Get value from cache."""
        self.value = self.cache.get(self.key)
        return self.value

    def get_or_compute(self, compute_func: CacheMissCallback) -> CacheValue:
        """
        Get value from cache or compute if missing.

        Args:
            compute_func: Function to compute value if cache miss

        Returns:
            Cached or computed value
        """
        value = self.cache.get(self.key, miss_callback=compute_func)
        if value is None:
            value = compute_func(self.key)
            if value is not None:
                self.set(value)
        self.value = value
        return value

    def set(self, value: CacheValue) -> bool:
        """Set value in cache."""
        self.value = value
        return self.cache.set(self.key, value, ttl=self.ttl)

    def delete(self) -> bool:
        """Delete value from cache."""
        return self.cache.delete(self.key)

    def exists(self) -> bool:
        """Check if key exists in cache."""
        return self.cache.exists(self.key)
