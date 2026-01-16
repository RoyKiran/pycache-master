"""Decorator-based API for caching."""

import functools
from typing import Any, Callable, Optional, TypeVar

from pycaching.api.factory import create_cache
from pycaching.core.config import CacheConfig
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.key_generation import generate_key

T = TypeVar("T")


def cache(
    ttl: Optional[float] = None,
    key_func: Optional[Callable[..., str]] = None,
    backend: Optional[str] = None,
    strategy: Optional[str] = None,
    config: Optional[CacheConfig] = None,
    cache_key_prefix: str = "",
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_func: Optional function to generate cache keys
        backend: Backend name ('memory', 'redis', etc.)
        strategy: Strategy name ('cache_aside', 'write_through', etc.)
        config: Optional CacheConfig instance
        cache_key_prefix: Prefix for cache keys

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create cache instance
        cache_instance = create_cache(
            backend=backend or "memory",
            strategy=strategy or "cache_aside",
            config=config,
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            if key_func is not None:
                key = key_func(*args, **kwargs)
            else:
                key = generate_key(
                    *args,
                    prefix=cache_key_prefix or func.__name__,
                    **kwargs,
                )

            # Try to get from cache
            cached_value = cache_instance.get(key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
