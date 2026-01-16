"""Validation utilities for cache operations."""

from typing import Any

from pycaching.core.exceptions import CacheKeyError
from pycaching.core.types import CacheKey, CacheValue


def validate_key(key: CacheKey) -> None:
    """
    Validate a cache key.

    Args:
        key: The cache key to validate

    Raises:
        CacheKeyError: If the key is invalid
    """
    if key is None:
        raise CacheKeyError("Cache key cannot be None")

    if isinstance(key, str) and not key:
        raise CacheKeyError("Cache key cannot be an empty string")

    if isinstance(key, bytes) and not key:
        raise CacheKeyError("Cache key cannot be empty bytes")


def validate_value(value: CacheValue) -> None:
    """
    Validate a cache value.

    Args:
        value: The cache value to validate

    Raises:
        ValueError: If the value is invalid
    """
    # For now, we accept any value
    # This can be extended to add specific validation rules
    pass


def validate_ttl(ttl: float) -> None:
    """
    Validate a TTL value.

    Args:
        ttl: The TTL in seconds

    Raises:
        ValueError: If the TTL is invalid
    """
    if ttl <= 0:
        raise ValueError("TTL must be positive")
    if not isinstance(ttl, (int, float)):
        raise ValueError("TTL must be a number")
