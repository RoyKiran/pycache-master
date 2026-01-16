"""TTL (Time To Live) strategy implementation."""

from typing import Optional

from typing import Optional

from pycaching.core.backend import Backend
from pycaching.core.exceptions import StrategyError
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback


class TTLStrategy(BaseStrategy):
    """Strategy that enforces TTL (Time To Live) for cache entries."""

    def __init__(self, default_ttl: Optional[float] = None, name: str = "ttl"):
        super().__init__(name)
        if default_ttl is not None and default_ttl <= 0:
            raise StrategyError("default_ttl must be positive")
        self.default_ttl = default_ttl

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value with TTL enforcement."""
        # Use provided TTL or fall back to default
        effective_ttl = ttl if ttl is not None else self.default_ttl
        if effective_ttl is None:
            raise StrategyError("TTL must be provided either as parameter or default_ttl")
        if effective_ttl <= 0:
            raise StrategyError("TTL must be positive")

        return backend.set(key, value, effective_ttl)

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, automatically handling expiration."""
        # The backend should handle expiration checking
        return super().get(backend, key, miss_callback)
