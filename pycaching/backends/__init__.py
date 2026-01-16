"""Backend implementations for various storage systems."""

from pycaching.backends.base import BaseBackend
from pycaching.backends.custom import CustomBackend
from pycaching.backends.file_backend import FileBackend
from pycaching.backends.memory import MemoryBackend
from pycaching.backends.memcached_backend import MemcachedBackend
from pycaching.backends.mongodb_backend import MongoDBBackend
from pycaching.backends.redis_backend import RedisBackend
from pycaching.backends.sqlite_backend import SQLiteBackend

__all__ = [
    "BaseBackend",
    "MemoryBackend",
    "FileBackend",
    "SQLiteBackend",
    "RedisBackend",
    "MemcachedBackend",
    "MongoDBBackend",
    "CustomBackend",
]

# Optional backends (may require additional dependencies)
try:
    from pycaching.backends.elasticache_backend import ElastiCacheBackend

    __all__.append("ElastiCacheBackend")
except ImportError:
    pass

try:
    from pycaching.backends.cloudflare_backend import CloudflareBackend

    __all__.append("CloudflareBackend")
except ImportError:
    pass
