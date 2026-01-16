"""Cloudflare KV backend implementation."""

from typing import Iterator, Optional
from threading import Lock

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class CloudflareBackend(BaseBackend):
    """Cloudflare KV backend for caching."""

    def __init__(
        self,
        account_id: str,
        namespace_id: str,
        api_token: str,
        serializer: Optional[Serializer] = None,
        name: str = "cloudflare",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        try:
            from cloudflare import Cloudflare
        except ImportError:
            raise ImportError(
                "cloudflare is required for CloudflareBackend. Install with: pip install cloudflare"
            )

        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()

        # Initialize Cloudflare client
        self.client = Cloudflare(api_token=api_token)
        self.account_id = account_id
        self.namespace_id = namespace_id

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from Cloudflare KV."""
        key_str = str(key)

        try:
            with self._lock:
                response = self.client.accounts.kv.namespaces.values.get(
                    account_id=self.account_id,
                    namespace_id=self.namespace_id,
                    key=key_str,
                )
                if response is None:
                    return None
                data = response.content if hasattr(response, "content") else response
                return self.serializer.deserialize(data)
        except Exception as e:
            # Cloudflare returns 404 for missing keys
            if "404" in str(e) or "not found" in str(e).lower():
                return None
            raise BackendError(f"Failed to get value from Cloudflare KV: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in Cloudflare KV."""
        key_str = str(key)

        try:
            with self._lock:
                data = self.serializer.serialize(value)
                expiration_ttl = int(ttl) if ttl is not None else None

                self.client.accounts.kv.namespaces.values.put(
                    account_id=self.account_id,
                    namespace_id=self.namespace_id,
                    key=key_str,
                    value=data,
                    expiration_ttl=expiration_ttl,
                )
                return True
        except Exception as e:
            raise BackendError(f"Failed to set value in Cloudflare KV: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from Cloudflare KV."""
        key_str = str(key)

        try:
            with self._lock:
                self.client.accounts.kv.namespaces.values.delete(
                    account_id=self.account_id,
                    namespace_id=self.namespace_id,
                    key=key_str,
                )
                return True
        except Exception as e:
            raise BackendError(f"Failed to delete value from Cloudflare KV: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in Cloudflare KV."""
        return self._get_impl(key) is not None

    def _clear_impl(self) -> bool:
        """Clear all entries from Cloudflare KV."""
        # Cloudflare KV doesn't support bulk delete
        # This would need to list all keys and delete them individually
        raise BackendError("Cloudflare KV does not support bulk clear operation")

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from Cloudflare KV."""
        try:
            with self._lock:
                # Cloudflare KV list operation
                response = self.client.accounts.kv.namespaces.keys.list(
                    account_id=self.account_id,
                    namespace_id=self.namespace_id,
                )
                keys_list = response.result if hasattr(response, "result") else []

                for key_info in keys_list:
                    key = key_info.name if hasattr(key_info, "name") else str(key_info)
                    if pattern is None:
                        yield key
                    else:
                        import fnmatch
                        if fnmatch.fnmatch(key, pattern):
                            yield key
        except Exception as e:
            raise BackendError(f"Failed to get keys from Cloudflare KV: {e}") from e

    def size(self) -> int:
        """Get the number of entries in Cloudflare KV."""
        try:
            with self._lock:
                response = self.client.accounts.kv.namespaces.keys.list(
                    account_id=self.account_id,
                    namespace_id=self.namespace_id,
                )
                keys_list = response.result if hasattr(response, "result") else []
                return len(keys_list)
        except Exception as e:
            raise BackendError(f"Failed to get size from Cloudflare KV: {e}") from e

    def close(self) -> None:
        """Close Cloudflare connection."""
        super().close()
        # Cloudflare client doesn't need explicit closing
        pass
