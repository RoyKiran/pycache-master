"""Base strategy implementation."""

from typing import Optional

from pycaching.core.backend import Backend
from pycaching.core.strategy import BaseStrategy as CoreBaseStrategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class BaseStrategy(CoreBaseStrategy):
    """Enhanced base strategy with common functionality."""

    def __init__(self, name: str = "base"):
        super().__init__(name)

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value using the strategy."""
        self._validate_backend(backend)
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
        """Set a value using the strategy."""
        self._validate_backend(backend)
        return backend.set(key, value, ttl)

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a value using the strategy."""
        self._validate_backend(backend)
        return backend.delete(key)
