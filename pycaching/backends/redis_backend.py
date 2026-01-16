"""Redis backend implementation with connection pooling."""

from typing import Iterator, Optional
from threading import Lock
from datetime import timedelta

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class RedisBackend(BaseBackend):
    """Redis backend with connection pooling."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 50,
        serializer: Optional[Serializer] = None,
        name: str = "redis",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        try:
            import redis
            from redis.connection import ConnectionPool
        except ImportError:
            raise ImportError(
                "redis is required for RedisBackend. Install with: pip install redis"
            )

        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()

        # Create connection pool
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=False,  # We handle serialization ourselves
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from Redis."""
        key_str = str(key).encode("utf-8")

        try:
            with self._lock:
                data = self.client.get(key_str)
                if data is None:
                    return None
                return self.serializer.deserialize(data)
        except Exception as e:
            raise BackendError(f"Failed to get value from Redis: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in Redis."""
        key_str = str(key).encode("utf-8")

        try:
            with self._lock:
                data = self.serializer.serialize(value)
                if ttl is not None:
                    self.client.setex(key_str, int(ttl), data)
                else:
                    self.client.set(key_str, data)
                return True
        except Exception as e:
            raise BackendError(f"Failed to set value in Redis: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from Redis."""
        key_str = str(key).encode("utf-8")

        try:
            with self._lock:
                deleted = self.client.delete(key_str)
                return deleted > 0
        except Exception as e:
            raise BackendError(f"Failed to delete value from Redis: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in Redis."""
        key_str = str(key).encode("utf-8")

        try:
            with self._lock:
                return bool(self.client.exists(key_str))
        except Exception as e:
            raise BackendError(f"Failed to check existence in Redis: {e}") from e

    def _clear_impl(self) -> bool:
        """Clear all entries from Redis."""
        try:
            with self._lock:
                self.client.flushdb()
                return True
        except Exception as e:
            raise BackendError(f"Failed to clear Redis: {e}") from e

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from Redis."""
        try:
            with self._lock:
                pattern_str = pattern.encode("utf-8") if pattern else b"*"
                for key_bytes in self.client.scan_iter(match=pattern_str):
                    yield key_bytes.decode("utf-8")
        except Exception as e:
            raise BackendError(f"Failed to get keys from Redis: {e}") from e

    def size(self) -> int:
        """Get the number of entries in Redis."""
        try:
            with self._lock:
                return self.client.dbsize()
        except Exception as e:
            raise BackendError(f"Failed to get size from Redis: {e}") from e

    def close(self) -> None:
        """Close Redis connection pool."""
        super().close()
        if hasattr(self, "pool"):
            self.pool.disconnect()
