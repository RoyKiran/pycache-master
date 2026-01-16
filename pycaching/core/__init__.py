"""Core abstractions and interfaces for the caching library."""

from pycaching.core.backend import AsyncBackend, Backend
from pycaching.core.cache import CacheManager as CoreCacheManager
from pycaching.core.config import CacheConfig
from pycaching.core.exceptions import (
    CacheError,
    CacheKeyError,
    CacheSerializationError,
    CacheTimeoutError,
    BackendError,
    StrategyError,
)
from pycaching.core.strategy import AsyncStrategy, Strategy
from pycaching.core.types import CacheEntry, CacheKey, CacheValue, Serializer

__all__ = [
    "Backend",
    "AsyncBackend",
    "Strategy",
    "AsyncStrategy",
    "CoreCacheManager",
    "CacheConfig",
    "CacheError",
    "BackendError",
    "StrategyError",
    "CacheKeyError",
    "CacheSerializationError",
    "CacheTimeoutError",
    "CacheEntry",
    "CacheKey",
    "CacheValue",
    "Serializer",
]
