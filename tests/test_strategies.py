"""Unit tests for caching strategies."""

import pytest

from pycaching.backends.memory import MemoryBackend
from pycaching.strategies.cache_aside import CacheAsideStrategy
from pycaching.strategies.ttl import TTLStrategy


def test_cache_aside_strategy():
    """Test cache-aside strategy."""
    backend = MemoryBackend()
    strategy = CacheAsideStrategy()

    # Test get with miss callback
    def miss_callback(key):
        return f"computed_{key}"

    value = strategy.get(backend, "key1", miss_callback=miss_callback)
    assert value == "computed_key1"

    # Should be cached now
    value = strategy.get(backend, "key1")
    assert value == "computed_key1"

    backend.close()


def test_ttl_strategy():
    """Test TTL strategy."""
    backend = MemoryBackend()
    strategy = TTLStrategy(default_ttl=0.1)

    # Set with default TTL
    strategy.set(backend, "key1", "value1")

    # Should exist
    assert backend.get("key1") == "value1"

    # Wait for expiration
    import time
    time.sleep(0.15)

    # Should be expired
    assert backend.get("key1") is None

    backend.close()
