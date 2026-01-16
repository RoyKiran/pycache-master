"""In-memory backend implementation using dictionary."""

from typing import Iterator, Optional
from threading import Lock

from pycaching.backends.base import BaseBackend
from pycaching.core.types import CacheKey, CacheValue


class MemoryBackend(BaseBackend):
    """In-memory backend using a dictionary for storage."""

    def __init__(self, name: str = "memory", enable_metadata: bool = True):
        super().__init__(name, enable_metadata)
        self._store: dict[CacheKey, CacheValue] = {}
        self._lock = Lock()

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the in-memory store."""
        with self._lock:
            return self._store.get(key)

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the in-memory store."""
        with self._lock:
            self._store[key] = value
            return True

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from the in-memory store."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in the in-memory store."""
        with self._lock:
            return key in self._store

    def _clear_impl(self) -> bool:
        """Clear all entries from the in-memory store."""
        with self._lock:
            self._store.clear()
            return True

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        with self._lock:
            keys_list = list(self._store.keys())

        if pattern is None:
            for key in keys_list:
                yield key
        else:
            # Simple pattern matching (supports * wildcard)
            import fnmatch

            for key in keys_list:
                key_str = str(key)
                if fnmatch.fnmatch(key_str, pattern):
                    yield key

    def size(self) -> int:
        """Get the number of entries in the cache."""
        with self._lock:
            return len(self._store)
