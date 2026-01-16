"""Integration tests for backend/strategy combinations."""

import pytest

from pycaching.backends.memory import MemoryBackend
from pycaching.core.cache import CacheManager
from pycaching.strategies.cache_aside import CacheAsideStrategy
from pycaching.strategies.write_through import WriteThroughStrategy
from pycaching.strategies.ttl import TTLStrategy


def test_memory_cache_aside_integration():
    """Test memory backend with cache-aside strategy."""
    backend = MemoryBackend()
    strategy = CacheAsideStrategy()
    manager = CacheManager(backend, strategy)

    def compute_value(key):
        return f"computed_{key}"

    # First get should compute
    value = manager.get("key1", miss_callback=compute_value)
    assert value == "computed_key1"

    # Second get should use cache
    value = manager.get("key1")
    assert value == "computed_key1"

    manager.close()


def test_memory_ttl_integration():
    """Test memory backend with TTL strategy."""
    backend = MemoryBackend()
    strategy = TTLStrategy(default_ttl=0.1)
    manager = CacheManager(backend, strategy)

    manager.set("key1", "value1")
    assert manager.get("key1") == "value1"

    # Wait for expiration
    import time
    time.sleep(0.15)

    assert manager.get("key1") is None

    manager.close()


def test_write_through_integration():
    """Test write-through strategy integration."""
    backend = MemoryBackend()
    write_calls = []

    def write_callback(key, value):
        write_calls.append((key, value))

    strategy = WriteThroughStrategy(write_callback=write_callback)
    manager = CacheManager(backend, strategy)

    manager.set("key1", "value1")
    assert len(write_calls) == 1
    assert write_calls[0] == ("key1", "value1")

    manager.close()
