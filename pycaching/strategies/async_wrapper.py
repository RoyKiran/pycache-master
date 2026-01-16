"""Async wrapper for sync strategies."""

from typing import Optional
import asyncio

from pycaching.core.backend import AsyncBackend, Backend
from pycaching.core.strategy import AsyncStrategy, Strategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback
from pycaching.backends.async_wrapper import AsyncBackendWrapper


class AsyncStrategyWrapper(AsyncStrategy):
    """Wrapper to make a sync strategy async."""

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    async def get(
        self,
        backend: AsyncBackend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value using the strategy."""
        # If backend is a wrapper, unwrap it
        if isinstance(backend, AsyncBackendWrapper):
            sync_backend = backend.backend
        else:
            # For native async backends, we need to call async methods
            return await backend.get(key)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.strategy.get, sync_backend, key, miss_callback
        )

    async def set(
        self,
        backend: AsyncBackend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value using the strategy."""
        if isinstance(backend, AsyncBackendWrapper):
            sync_backend = backend.backend
        else:
            return await backend.set(key, value, ttl)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.strategy.set, sync_backend, key, value, ttl
        )

    async def delete(self, backend: AsyncBackend, key: CacheKey) -> bool:
        """Delete a value using the strategy."""
        if isinstance(backend, AsyncBackendWrapper):
            sync_backend = backend.backend
        else:
            return await backend.delete(key)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.strategy.delete, sync_backend, key)

    async def clear(self, backend: AsyncBackend) -> bool:
        """Clear the cache using the strategy."""
        if isinstance(backend, AsyncBackendWrapper):
            sync_backend = backend.backend
        else:
            return await backend.clear()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.strategy.clear, sync_backend)
