"""Async cache manager implementation."""

from typing import Any, AsyncIterator, Optional

from pycaching.core.backend import AsyncBackend
from pycaching.core.config import CacheConfig
from pycaching.core.strategy import AsyncStrategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback
from pycaching.utils.key_generation import generate_key


class AsyncCacheManager:
    """Async cache manager that combines backends and strategies."""

    def __init__(
        self,
        backend: AsyncBackend,
        strategy: AsyncStrategy,
        config: Optional[CacheConfig] = None,
    ):
        self.backend = backend
        self.strategy = strategy
        self.config = config or CacheConfig()

    async def get(
        self,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value from the cache."""
        full_key = self._make_key(key)
        return await self.strategy.get(self.backend, full_key, miss_callback)

    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        full_key = self._make_key(key)
        ttl = ttl or self.config.default_ttl
        return await self.strategy.set(self.backend, full_key, value, ttl)

    async def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        full_key = self._make_key(key)
        return await self.strategy.delete(self.backend, full_key)

    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        full_key = self._make_key(key)
        return await self.backend.exists(full_key)

    async def clear(self) -> bool:
        """Clear all entries from the cache."""
        return await self.strategy.clear(self.backend)

    async def keys(self, pattern: Optional[str] = None) -> AsyncIterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        async for key in self.backend.keys(pattern):
            yield key

    async def size(self) -> int:
        """Get the number of entries in the cache."""
        return await self.backend.size()

    def _make_key(self, key: CacheKey) -> CacheKey:
        """Generate a full cache key with prefix and namespace."""
        key_str = str(key)
        parts = []
        if self.config.namespace:
            parts.append(self.config.namespace)
        if self.config.key_prefix:
            parts.append(self.config.key_prefix)
        parts.append(key_str)
        return ":".join(parts)

    async def close(self) -> None:
        """Close the cache manager and backend."""
        await self.backend.close()

    async def __aenter__(self) -> "AsyncCacheManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
