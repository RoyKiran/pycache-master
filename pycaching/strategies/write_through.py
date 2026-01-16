"""Write-through strategy implementation."""

from typing import Callable, Optional

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue


WriteCallback = Callable[[CacheKey, CacheValue], None]


class WriteThroughStrategy(BaseStrategy):
    """
    Write-through strategy.

    Data is written to both the cache and the underlying data store simultaneously.
    """

    def __init__(
        self,
        write_callback: Optional[WriteCallback] = None,
        name: str = "write_through",
    ):
        super().__init__(name)
        self.write_callback = write_callback

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value, writing to both cache and data store."""
        # Write to underlying data store first
        if self.write_callback is not None:
            try:
                self.write_callback(key, value)
            except Exception as e:
                # If write to data store fails, don't update cache
                raise RuntimeError(f"Failed to write to data store: {e}") from e

        # Then write to cache
        return backend.set(key, value, ttl)
