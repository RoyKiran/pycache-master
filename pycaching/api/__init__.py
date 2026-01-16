"""Public API layers for different usage patterns."""

from pycaching.api.context import CacheContext
from pycaching.api.decorator import cache as cache_decorator
from pycaching.api.factory import create_cache
from pycaching.api.functional import cache
from pycaching.api.manager import CacheManager

__all__ = [
    "CacheManager",
    "CacheContext",
    "cache",
    "cache_decorator",
    "create_cache",
]
