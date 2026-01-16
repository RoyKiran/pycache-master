"""Async wrapper for sync backends."""

from typing import AsyncIterator, Optional
import asyncio

from pycaching.core.backend import AsyncBackend, Backend
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.async_helpers import sync_to_async


class AsyncBackendWrapper(AsyncBackend):
    """Wrapper to make a sync backend async."""

    def __init__(self, backend: Backend):
        self.backend = backend
        self._executor = None

    async def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.get, key)

    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.set, key, value, ttl)

    async def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.delete, key)

    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.exists, key)

    async def clear(self) -> bool:
        """Clear all entries from the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.clear)

    async def keys(self, pattern: Optional[str] = None) -> AsyncIterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        loop = asyncio.get_event_loop()
        keys_list = await loop.run_in_executor(None, list, self.backend.keys(pattern))
        for key in keys_list:
            yield key

    async def size(self) -> int:
        """Get the number of entries in the cache."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.backend.size)

    async def close(self) -> None:
        """Close the backend connection."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.backend.close)
