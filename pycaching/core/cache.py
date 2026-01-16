"""Main cache manager implementation."""

from typing import Any, Iterator, Optional
from threading import Lock

from pycaching.core.backend import Backend
from pycaching.core.config import CacheConfig
from pycaching.core.exceptions import CacheError
from pycaching.core.strategy import Strategy
from pycaching.core.types import CacheKey, CacheValue, CacheMissCallback
from pycaching.utils.key_generation import generate_key


class CacheManager:
    """Main cache manager that combines backends and strategies."""

    def __init__(
        self,
        backend: Backend,
        strategy: Strategy,
        config: Optional[CacheConfig] = None,
    ):
        self.backend = backend
        self.strategy = strategy
        self.config = config or CacheConfig()
        self._lock = Lock()

    def get(
        self,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value from the cache."""
        full_key = self._make_key(key)
        with self._lock:
            return self.strategy.get(self.backend, full_key, miss_callback)

    def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        full_key = self._make_key(key)
        ttl = ttl or self.config.default_ttl
        with self._lock:
            return self.strategy.set(self.backend, full_key, value, ttl)

    def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        full_key = self._make_key(key)
        with self._lock:
            return self.strategy.delete(self.backend, full_key)

    def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        full_key = self._make_key(key)
        with self._lock:
            return self.backend.exists(full_key)

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        with self._lock:
            return self.strategy.clear(self.backend)

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys, optionally filtered by pattern."""
        with self._lock:
            return self.backend.keys(pattern)

    def size(self) -> int:
        """Get the number of entries in the cache."""
        with self._lock:
            return self.backend.size()

    def _make_key(self, key: CacheKey) -> CacheKey:
        """Generate a full cache key with prefix and namespace."""
        key_str = str(key)
        parts = []
        if self.config.namespace:
            parts.append(self.config.namespace)
        if self.config.key_prefix:
            parts.append(self.config.key_prefix)
        parts.append(key_str)
        return ":".join(parts)

    def close(self) -> None:
        """Close the cache manager and backend."""
        with self._lock:
            self.backend.close()

    def __enter__(self) -> "CacheManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def __getitem__(self, key: CacheKey) -> CacheValue:
        """Get item using dictionary-style access."""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key not found: {key}")
        return value

    def __setitem__(self, key: CacheKey, value: CacheValue) -> None:
        """Set item using dictionary-style access."""
        self.set(key, value)

    def __delitem__(self, key: CacheKey) -> None:
        """Delete item using dictionary-style access."""
        if not self.delete(key):
            raise KeyError(f"Key not found: {key}")

    def __contains__(self, key: CacheKey) -> bool:
        """Check if key exists using 'in' operator."""
        return self.exists(key)

    def __len__(self) -> int:
        """Get cache size using len()."""
        return self.size()
