"""Base backend implementation with common functionality."""

from typing import Any, Iterator, Optional
from datetime import datetime, timedelta

from pycaching.core.backend import BaseBackend as CoreBaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue, CacheMetadata


class BaseBackend(CoreBaseBackend):
    """Enhanced base backend with metadata support."""

    def __init__(self, name: str = "base", enable_metadata: bool = True):
        super().__init__(name)
        self.enable_metadata = enable_metadata
        self._metadata: dict[CacheKey, CacheMetadata] = {}

    def _get_metadata(self, key: CacheKey) -> Optional[CacheMetadata]:
        """Get metadata for a key."""
        if not self.enable_metadata:
            return None
        return self._metadata.get(key)

    def _set_metadata(
        self,
        key: CacheKey,
        ttl: Optional[float] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        """Set metadata for a key."""
        if not self.enable_metadata:
            return

        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)

        if key in self._metadata:
            metadata = self._metadata[key]
            metadata.expires_at = expires_at
            if tags:
                metadata.tags = tags
        else:
            self._metadata[key] = CacheMetadata(expires_at=expires_at, tags=tags or [])

    def _update_access_metadata(self, key: CacheKey) -> None:
        """Update access metadata for a key."""
        if self.enable_metadata and key in self._metadata:
            self._metadata[key].update_access()

    def _delete_metadata(self, key: CacheKey) -> None:
        """Delete metadata for a key."""
        if self.enable_metadata:
            self._metadata.pop(key, None)

    def _clear_metadata(self) -> None:
        """Clear all metadata."""
        if self.enable_metadata:
            self._metadata.clear()

    def _is_expired(self, key: CacheKey) -> bool:
        """Check if a key has expired."""
        if not self.enable_metadata:
            return False
        metadata = self._metadata.get(key)
        if metadata is None:
            return False
        return metadata.is_expired()

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from the cache."""
        self._check_closed()
        if self._is_expired(key):
            self.delete(key)
            return None
        value = self._get_impl(key)
        if value is not None:
            self._update_access_metadata(key)
        return value

    def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in the cache."""
        self._check_closed()
        result = self._set_impl(key, value, ttl)
        if result:
            self._set_metadata(key, ttl)
        return result

    def delete(self, key: CacheKey) -> bool:
        """Delete a value from the cache."""
        self._check_closed()
        result = self._delete_impl(key)
        if result:
            self._delete_metadata(key)
        return result

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        self._check_closed()
        result = self._clear_impl()
        if result:
            self._clear_metadata()
        return result

    def exists(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache."""
        self._check_closed()
        if self._is_expired(key):
            self.delete(key)
            return False
        return self._exists_impl(key)

    def close(self) -> None:
        """Close the backend connection."""
        super().close()
        self._clear_metadata()

    # Abstract methods that subclasses must implement
    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Implementation-specific get method."""
        raise NotImplementedError

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Implementation-specific set method."""
        raise NotImplementedError

    def _delete_impl(self, key: CacheKey) -> bool:
        """Implementation-specific delete method."""
        raise NotImplementedError

    def _exists_impl(self, key: CacheKey) -> bool:
        """Implementation-specific exists method."""
        raise NotImplementedError

    def _clear_impl(self) -> bool:
        """Implementation-specific clear method."""
        raise NotImplementedError
