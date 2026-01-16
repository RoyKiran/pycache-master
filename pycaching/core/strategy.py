"""Strategy protocol and base implementations."""

from typing import Any, Optional, Protocol
from abc import ABC, abstractmethod

from pycaching.core.backend import Backend, AsyncBackend
from pycaching.core.exceptions import StrategyError
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class Strategy(Protocol):
    """Protocol for caching strategies."""

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value using the strategy."""
        ...

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value using the strategy."""
        ...

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a value using the strategy."""
        ...

    def clear(self, backend: Backend) -> bool:
        """Clear the cache using the strategy."""
        ...


class AsyncStrategy(Protocol):
    """Protocol for asynchronous caching strategies."""

    async def get(
        self,
        backend: AsyncBackend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value using the strategy."""
        ...

    async def set(
        self,
        backend: AsyncBackend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value using the strategy."""
        ...

    async def delete(self, backend: AsyncBackend, key: CacheKey) -> bool:
        """Delete a value using the strategy."""
        ...

    async def clear(self, backend: AsyncBackend) -> bool:
        """Clear the cache using the strategy."""
        ...


class BaseStrategy(ABC):
    """Base class for strategy implementations."""

    def __init__(self, name: str = "base"):
        self.name = name

    @abstractmethod
    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value using the strategy."""
        pass

    @abstractmethod
    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value using the strategy."""
        pass

    @abstractmethod
    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a value using the strategy."""
        pass

    def clear(self, backend: Backend) -> bool:
        """Clear the cache using the strategy."""
        return backend.clear()

    def _validate_backend(self, backend: Any) -> None:
        """Validate that backend implements the required protocol."""
        if not hasattr(backend, "get") or not hasattr(backend, "set"):
            raise StrategyError(f"Backend does not implement required methods for {self.name}")
