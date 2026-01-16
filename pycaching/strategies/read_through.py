"""Read-through strategy implementation."""

from typing import Callable, Optional

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue


ReadCallback = Callable[[CacheKey], CacheValue]


class ReadThroughStrategy(BaseStrategy):
    """
    Read-through strategy.

    On cache miss, data is automatically loaded from the underlying data store
    and written to the cache.
    """

    def __init__(
        self,
        read_callback: Optional[ReadCallback] = None,
        name: str = "read_through",
    ):
        super().__init__(name)
        self.read_callback = read_callback

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, loading from data store on miss."""
        # Try to get from cache
        value = backend.get(key)

        # If miss, load from data store
        if value is None:
            callback = miss_callback or self.read_callback
            if callback is not None:
                try:
                    value = callback(key)
                    if value is not None:
                        # Store in cache for future requests
                        backend.set(key, value)
                except Exception as e:
                    raise RuntimeError(f"Failed to read from data store: {e}") from e

        return value
