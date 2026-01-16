"""File-based backend implementation."""

import json
import os
from pathlib import Path
from typing import Iterator, Optional
from threading import Lock

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class FileBackend(BaseBackend):
    """File-based backend that stores cache entries as files."""

    def __init__(
        self,
        cache_dir: str = ".cache",
        serializer: Optional[Serializer] = None,
        name: str = "file",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        self.cache_dir = Path(cache_dir)
        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: CacheKey) -> Path:
        """Get the file path for a key."""
        # Sanitize key to be filesystem-safe
        key_str = str(key).replace("/", "_").replace("\\", "_")
        # Use hash for very long keys
        if len(key_str) > 200:
            from pycaching.utils.key_generation import hash_key
            key_str = hash_key(key_str)
        return self.cache_dir / f"{key_str}.cache"

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from a file."""
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return None

        try:
            with self._lock:
                with open(file_path, "rb") as f:
                    data = f.read()
                value = self.serializer.deserialize(data)
                return value
        except Exception as e:
            raise BackendError(f"Failed to read cache file: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value to a file."""
        file_path = self._get_file_path(key)
        try:
            with self._lock:
                data = self.serializer.serialize(value)
                with open(file_path, "wb") as f:
                    f.write(data)

                # Store TTL in metadata file if needed
                if ttl is not None and self.enable_metadata:
                    metadata_path = file_path.with_suffix(".meta")
                    metadata = {"ttl": ttl, "created_at": None}  # Simplified
                    with open(metadata_path, "w") as f:
                        json.dump(metadata, f)

            return True
        except Exception as e:
            raise BackendError(f"Failed to write cache file: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value file."""
        file_path = self._get_file_path(key)
        metadata_path = file_path.with_suffix(".meta")

        try:
            with self._lock:
                deleted = False
                if file_path.exists():
                    file_path.unlink()
                    deleted = True
                if metadata_path.exists():
                    metadata_path.unlink()
                return deleted
        except Exception as e:
            raise BackendError(f"Failed to delete cache file: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a cache file exists."""
        file_path = self._get_file_path(key)
        return file_path.exists()

    def _clear_impl(self) -> bool:
        """Clear all cache files."""
        try:
            with self._lock:
                for file_path in self.cache_dir.glob("*.cache"):
                    file_path.unlink()
                for file_path in self.cache_dir.glob("*.meta"):
                    file_path.unlink()
            return True
        except Exception as e:
            raise BackendError(f"Failed to clear cache directory: {e}") from e

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from cache files."""
        with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                # Extract key from filename (simplified)
                key = file_path.stem
                if pattern is None:
                    yield key
                else:
                    import fnmatch
                    if fnmatch.fnmatch(key, pattern):
                        yield key

    def size(self) -> int:
        """Get the number of cache files."""
        with self._lock:
            return len(list(self.cache_dir.glob("*.cache")))
