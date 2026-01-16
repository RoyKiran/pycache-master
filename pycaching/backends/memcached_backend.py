"""Memcached backend implementation with connection pooling."""

from typing import Iterator, Optional
from threading import Lock

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class MemcachedBackend(BaseBackend):
    """Memcached backend with connection pooling."""

    def __init__(
        self,
        servers: list[str] = None,
        serializer: Optional[Serializer] = None,
        name: str = "memcached",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        try:
            from pymemcache.client.base import Client
            from pymemcache.client.hash import HashClient
        except ImportError:
            raise ImportError(
                "pymemcache is required for MemcachedBackend. Install with: pip install pymemcache"
            )

        if servers is None:
            servers = ["localhost:11211"]

        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()

        # Create client (use HashClient for multiple servers)
        if len(servers) > 1:
            self.client = HashClient(servers)
        else:
            host, port = servers[0].split(":") if ":" in servers[0] else (servers[0], 11211)
            self.client = Client((host, int(port)))

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from Memcached."""
        key_str = str(key)

        try:
            with self._lock:
                data = self.client.get(key_str)
                if data is None:
                    return None
                return self.serializer.deserialize(data)
        except Exception as e:
            raise BackendError(f"Failed to get value from Memcached: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in Memcached."""
        key_str = str(key)

        try:
            with self._lock:
                data = self.serializer.serialize(value)
                # Memcached TTL is in seconds (max 30 days)
                expire = int(ttl) if ttl is not None else 0
                self.client.set(key_str, data, expire=expire)
                return True
        except Exception as e:
            raise BackendError(f"Failed to set value in Memcached: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from Memcached."""
        key_str = str(key)

        try:
            with self._lock:
                return self.client.delete(key_str)
        except Exception as e:
            raise BackendError(f"Failed to delete value from Memcached: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in Memcached."""
        key_str = str(key)

        try:
            with self._lock:
                return self.client.get(key_str) is not None
        except Exception as e:
            raise BackendError(f"Failed to check existence in Memcached: {e}") from e

    def _clear_impl(self) -> bool:
        """Clear all entries from Memcached."""
        try:
            with self._lock:
                self.client.flush_all()
                return True
        except Exception as e:
            raise BackendError(f"Failed to clear Memcached: {e}") from e

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from Memcached."""
        # Memcached doesn't support key listing natively
        # This is a limitation of Memcached protocol
        # Return empty iterator or raise error
        raise BackendError("Memcached does not support key listing")

    def size(self) -> int:
        """Get the number of entries in Memcached."""
        # Memcached doesn't support size counting natively
        # Return 0 or raise error
        raise BackendError("Memcached does not support size counting")

    def close(self) -> None:
        """Close Memcached connection."""
        super().close()
        if hasattr(self, "client"):
            self.client.close()
