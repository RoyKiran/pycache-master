"""Functional API for caching."""

from typing import Iterator, Optional

from pycaching.api.factory import create_cache
from pycaching.core.config import CacheConfig
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback

# Global cache instance (lazy initialized)
_global_cache = None
_global_config: Optional[CacheConfig] = None


def _get_cache():
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = create_cache(config=_global_config)
    return _global_cache


def configure(config: CacheConfig) -> None:
    """
    Configure the global cache instance.

    Args:
        config: CacheConfig instance
    """
    global _global_config, _global_cache
    _global_config = config
    _global_cache = None  # Reset cache to use new config


def get(
    key: CacheKey,
    miss_callback: Optional[CacheMissCallback] = None,
) -> Optional[CacheValue]:
    """
    Get a value from the global cache.

    Args:
        key: Cache key
        miss_callback: Optional callback if cache miss

    Returns:
        Cached value or None
    """
    return _get_cache().get(key, miss_callback=miss_callback)


def set(
    key: CacheKey,
    value: CacheValue,
    ttl: Optional[float] = None,
) -> bool:
    """
    Set a value in the global cache.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Optional time-to-live in seconds

    Returns:
        True if successfully set
    """
    return _get_cache().set(key, value, ttl=ttl)


def delete(key: CacheKey) -> bool:
    """
    Delete a value from the global cache.

    Args:
        key: Cache key

    Returns:
        True if successfully deleted
    """
    return _get_cache().delete(key)


def exists(key: CacheKey) -> bool:
    """
    Check if a key exists in the global cache.

    Args:
        key: Cache key

    Returns:
        True if key exists
    """
    return _get_cache().exists(key)


def clear() -> bool:
    """
    Clear all entries from the global cache.

    Returns:
        True if successfully cleared
    """
    return _get_cache().clear()


def keys(pattern: Optional[str] = None) -> Iterator[CacheKey]:
    """
    Get all keys from the global cache.

    Args:
        pattern: Optional pattern to filter keys

    Returns:
        Iterator of cache keys
    """
    return _get_cache().keys(pattern)


def size() -> int:
    """
    Get the number of entries in the global cache.

    Returns:
        Number of entries
    """
    return _get_cache().size()


# Create a cache object for functional API
class Cache:
    """Functional cache API object."""

    get = staticmethod(get)
    set = staticmethod(set)
    delete = staticmethod(delete)
    exists = staticmethod(exists)
    clear = staticmethod(clear)
    keys = staticmethod(keys)
    size = staticmethod(size)
    configure = staticmethod(configure)


# Global cache instance for functional API
cache = Cache()
