"""Class-based API for cache management."""

from typing import Iterator, Optional

from pycaching.core.backend import Backend
from pycaching.core.cache import CacheManager as CoreCacheManager
from pycaching.core.config import CacheConfig
from pycaching.core.strategy import Strategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class CacheManager(CoreCacheManager):
    """
    High-level cache manager with additional convenience methods.

    This extends the core CacheManager with additional utility methods.
    """

    def get_or_set(
        self,
        key: CacheKey,
        default: CacheValue,
        ttl: Optional[float] = None,
    ) -> CacheValue:
        """
        Get a value from cache, or set and return default if missing.

        Args:
            key: Cache key
            default: Default value to set if missing
            ttl: Optional time-to-live

        Returns:
            Cached value or default
        """
        value = self.get(key)
        if value is None:
            self.set(key, default, ttl=ttl)
            return default
        return value

    def get_or_compute(
        self,
        key: CacheKey,
        compute_func: CacheMissCallback,
        ttl: Optional[float] = None,
    ) -> CacheValue:
        """
        Get a value from cache, or compute and cache if missing.

        Args:
            key: Cache key
            compute_func: Function to compute value if missing
            ttl: Optional time-to-live

        Returns:
            Cached or computed value
        """
        value = self.get(key, miss_callback=compute_func)
        if value is None:
            value = compute_func(key)
            if value is not None:
                self.set(key, value, ttl=ttl)
        return value

    def set_many(self, mapping: dict[CacheKey, CacheValue], ttl: Optional[float] = None) -> int:
        """
        Set multiple key-value pairs.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Optional time-to-live for all entries

        Returns:
            Number of successfully set entries
        """
        count = 0
        for key, value in mapping.items():
            if self.set(key, value, ttl=ttl):
                count += 1
        return count

    def get_many(self, keys: list[CacheKey]) -> dict[CacheKey, Optional[CacheValue]]:
        """
        Get multiple values.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs (None for missing keys)
        """
        result = {}
        for key in keys:
            result[key] = self.get(key)
        return result

    def delete_many(self, keys: list[CacheKey]) -> int:
        """
        Delete multiple keys.

        Args:
            keys: List of cache keys to delete

        Returns:
            Number of successfully deleted keys
        """
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count
