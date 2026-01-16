"""Key generation and hashing utilities."""

import hashlib
import json
from typing import Any, Callable, Optional

from pycaching.core.types import CacheKey


def hash_key(key: CacheKey, algorithm: str = "sha256") -> str:
    """
    Hash a cache key to a fixed-length string.

    Args:
        key: The cache key to hash
        algorithm: Hash algorithm to use (sha256, md5, etc.)

    Returns:
        Hashed key as hexadecimal string
    """
    key_str = _key_to_string(key)
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(key_str.encode("utf-8"))
    return hash_obj.hexdigest()


def generate_key(
    *args: Any,
    prefix: Optional[str] = None,
    separator: str = ":",
    key_func: Optional[Callable[[Any], str]] = None,
    **kwargs: Any,
) -> str:
    """
    Generate a cache key from arguments.

    Args:
        *args: Positional arguments to include in key
        prefix: Optional prefix for the key
        separator: Separator between key parts
        key_func: Optional function to convert values to strings
        **kwargs: Keyword arguments to include in key

    Returns:
        Generated cache key string
    """
    parts = []

    if prefix:
        parts.append(prefix)

    # Add positional arguments
    for arg in args:
        parts.append(_value_to_string(arg, key_func))

    # Add keyword arguments (sorted for consistency)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for key, value in sorted_kwargs:
            parts.append(f"{key}={_value_to_string(value, key_func)}")

    return separator.join(parts)


def _key_to_string(key: CacheKey) -> str:
    """Convert a cache key to string."""
    if isinstance(key, str):
        return key
    elif isinstance(key, bytes):
        return key.decode("utf-8", errors="replace")
    elif isinstance(key, (int, float)):
        return str(key)
    else:
        return str(key)


def _value_to_string(value: Any, key_func: Optional[Callable[[Any], str]] = None) -> str:
    """Convert a value to string for key generation."""
    if key_func is not None:
        return key_func(value)

    if isinstance(value, (str, int, float, bool)):
        return str(value)
    elif isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    elif isinstance(value, (list, tuple)):
        return json.dumps(list(value), sort_keys=True)
    elif isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    else:
        # For complex objects, use their string representation
        return str(value)
