"""Backend protocol and base implementations."""

from typing import Any, AsyncIterator, Iterator, Optional, Protocol
from abc import ABC, abstractmethod

from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue


class Backend(Protocol):
    """Protocol for synchronous cache backends."""

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the cache."""
        ...

    def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        ...

    def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        ...

    def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        ...

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        ...

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        ...

    def size(self) -> int:
        """Get the number of entries in the cache."""
        ...

    def close(self) -> None:
        """Close the backend connection."""
        ...


class AsyncBackend(Protocol):
    """Protocol for asynchronous cache backends."""

    async def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the cache."""
        ...

    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        ...

    async def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        ...

    async def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        ...

    async def clear(self) -> bool:
        """Clear all entries from the cache."""
        ...

    async def keys(self, pattern: Optional[str] = None) -> AsyncIterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        ...

    async def size(self) -> int:
        """Get the number of entries in the cache."""
        ...

    async def close(self) -> None:
        """Close the backend connection."""
        ...


class BaseBackend(ABC):
    """Base class for backend implementations."""

    def __init__(self, name: str = "base"):
        self.name = name
        self._closed = False

    @abstractmethod
    def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the cache."""
        pass

    @abstractmethod
    def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        pass

    @abstractmethod
    def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        pass

    @abstractmethod
    def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all entries from the cache."""
        pass

    @abstractmethod
    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get the number of entries in the cache."""
        pass

    def close(self) -> None:
        """Close the backend connection."""
        self._closed = True

    def _check_closed(self) -> None:
        """Check if the backend is closed."""
        if self._closed:
            raise BackendError(f"Backend {self.name} is closed")

    def __enter__(self) -> "BaseBackend":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
