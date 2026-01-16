"""MongoDB backend implementation."""

from typing import Iterator, Optional
from threading import Lock
from datetime import datetime, timedelta

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class MongoDBBackend(BaseBackend):
    """MongoDB backend for caching."""

    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017/",
        database: str = "cache",
        collection: str = "entries",
        serializer: Optional[Serializer] = None,
        name: str = "mongodb",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        try:
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(
                "pymongo is required for MongoDBBackend. Install with: pip install pymongo"
            )

        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()

        # Create MongoDB client and collection
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]

        # Create indexes
        self.collection.create_index("key", unique=True)
        self.collection.create_index("expires_at", expireAfterSeconds=0)

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from MongoDB."""
        key_str = str(key)

        try:
            with self._lock:
                doc = self.collection.find_one({"key": key_str})
                if doc is None:
                    return None

                # Check expiration
                if doc.get("expires_at") and datetime.now() >= doc["expires_at"]:
                    self.collection.delete_one({"key": key_str})
                    return None

                # Deserialize value
                value_data = doc["value"]
                return self.serializer.deserialize(value_data)
        except Exception as e:
            raise BackendError(f"Failed to get value from MongoDB: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in MongoDB."""
        key_str = str(key)

        try:
            with self._lock:
                # Serialize value
                value_data = self.serializer.serialize(value)

                # Calculate expiration
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.now() + timedelta(seconds=ttl)

                # Insert or update
                self.collection.update_one(
                    {"key": key_str},
                    {
                        "$set": {
                            "key": key_str,
                            "value": value_data,
                            "expires_at": expires_at,
                            "updated_at": datetime.now(),
                        }
                    },
                    upsert=True,
                )
                return True
        except Exception as e:
            raise BackendError(f"Failed to set value in MongoDB: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from MongoDB."""
        key_str = str(key)

        try:
            with self._lock:
                result = self.collection.delete_one({"key": key_str})
                return result.deleted_count > 0
        except Exception as e:
            raise BackendError(f"Failed to delete value from MongoDB: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in MongoDB."""
        key_str = str(key)

        try:
            with self._lock:
                return self.collection.count_documents({"key": key_str}) > 0
        except Exception as e:
            raise BackendError(f"Failed to check existence in MongoDB: {e}") from e

    def _clear_impl(self) -> bool:
        """Clear all entries from MongoDB."""
        try:
            with self._lock:
                self.collection.delete_many({})
                return True
        except Exception as e:
            raise BackendError(f"Failed to clear MongoDB: {e}") from e

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from MongoDB."""
        try:
            with self._lock:
                query = {}
                if pattern:
                    # MongoDB regex pattern matching
                    import re
                    query = {"key": {"$regex": pattern.replace("*", ".*")}}

                for doc in self.collection.find(query, {"key": 1}):
                    yield doc["key"]
        except Exception as e:
            raise BackendError(f"Failed to get keys from MongoDB: {e}") from e

    def size(self) -> int:
        """Get the number of entries in MongoDB."""
        try:
            with self._lock:
                return self.collection.count_documents({})
        except Exception as e:
            raise BackendError(f"Failed to get size from MongoDB: {e}") from e

    def close(self) -> None:
        """Close MongoDB connection."""
        super().close()
        if hasattr(self, "client"):
            self.client.close()
