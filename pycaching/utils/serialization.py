"""Serialization utilities for cache values."""

import json
import pickle
from typing import Any, Protocol

from pycaching.core.exceptions import CacheSerializationError
from pycaching.core.types import CacheValue, Serializer


class PickleSerializer:
    """Pickle-based serializer."""

    def serialize(self, value: CacheValue) -> bytes:
        """Serialize a value using pickle."""
        try:
            return pickle.dumps(value)
        except Exception as e:
            raise CacheSerializationError(f"Failed to serialize value: {e}") from e

    def deserialize(self, data: bytes) -> CacheValue:
        """Deserialize bytes using pickle."""
        try:
            return pickle.loads(data)
        except Exception as e:
            raise CacheSerializationError(f"Failed to deserialize value: {e}") from e


class JSONSerializer:
    """JSON-based serializer."""

    def __init__(self, use_orjson: bool = True):
        self.use_orjson = use_orjson
        if use_orjson:
            try:
                import orjson
                self._orjson = orjson
            except ImportError:
                self.use_orjson = False

    def serialize(self, value: CacheValue) -> bytes:
        """Serialize a value using JSON."""
        try:
            if self.use_orjson:
                return self._orjson.dumps(value)
            else:
                return json.dumps(value).encode("utf-8")
        except Exception as e:
            raise CacheSerializationError(f"Failed to serialize value: {e}") from e

    def deserialize(self, data: bytes) -> CacheValue:
        """Deserialize bytes using JSON."""
        try:
            if self.use_orjson:
                return self._orjson.loads(data)
            else:
                return json.loads(data.decode("utf-8"))
        except Exception as e:
            raise CacheSerializationError(f"Failed to deserialize value: {e}") from e


class MsgPackSerializer:
    """MessagePack-based serializer."""

    def __init__(self):
        try:
            import msgpack
            self._msgpack = msgpack
        except ImportError:
            raise ImportError(
                "msgpack is required for MsgPackSerializer. Install with: pip install msgpack"
            )

    def serialize(self, value: CacheValue) -> bytes:
        """Serialize a value using MessagePack."""
        try:
            return self._msgpack.packb(value)
        except Exception as e:
            raise CacheSerializationError(f"Failed to serialize value: {e}") from e

    def deserialize(self, data: bytes) -> CacheValue:
        """Deserialize bytes using MessagePack."""
        try:
            return self._msgpack.unpackb(data, raw=False)
        except Exception as e:
            raise CacheSerializationError(f"Failed to deserialize value: {e}") from e


# Alias for backward compatibility
Serializer = Serializer
