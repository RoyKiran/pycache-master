"""
pycaching - Modular Python caching library for microservices, databases, and LLM workflows.

This library provides a flexible, extensible caching system with multiple backends,
caching strategies, and LLM-specific features.
"""

__version__ = "0.1.0"

from pycaching.api.factory import create_cache
from pycaching.api.functional import cache
from pycaching.api.manager import CacheManager

__all__ = [
    "CacheManager",
    "cache",
    "create_cache",
    "__version__",
]
