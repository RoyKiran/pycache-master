"""Custom backend interface and template."""

from typing import Iterator, Optional

from pycaching.backends.base import BaseBackend
from pycaching.core.types import CacheKey, CacheValue


class CustomBackend(BaseBackend):
    """
    Template for creating custom backends.

    Subclass this class and implement the required methods.
    """

    def __init__(self, name: str = "custom", enable_metadata: bool = True):
        super().__init__(name, enable_metadata)

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """
        Implementation-specific get method.

        Override this method to implement your custom backend logic.
        """
        raise NotImplementedError("Subclass must implement _get_impl")

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """
        Implementation-specific set method.

        Override this method to implement your custom backend logic.
        """
        raise NotImplementedError("Subclass must implement _set_impl")

    def _delete_impl(self, key: CacheKey) -> bool:
        """
        Implementation-specific delete method.

        Override this method to implement your custom backend logic.
        """
        raise NotImplementedError("Subclass must implement _delete_impl")

    def _exists_impl(self, key: CacheKey) -> bool:
        """
        Implementation-specific exists method.

        Override this method to implement your custom backend logic.
        """
        raise NotImplementedError("Subclass must implement _exists_impl")

    def _clear_impl(self) -> bool:
        """
        Implementation-specific clear method.

        Override this method to implement your custom backend logic.
        """
        raise NotImplementedError("Subclass must implement _clear_impl")

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """
        Get all keys, optionally filtered by pattern.

        Override this method if your backend supports key listing.
        """
        raise NotImplementedError("Subclass must implement keys")

    def size(self) -> int:
        """
        Get the number of entries in the cache.

        Override this method if your backend supports size counting.
        """
        raise NotImplementedError("Subclass must implement size")
