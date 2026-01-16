"""Unit tests for memory backend."""

import pytest

from pycaching.backends.memory import MemoryBackend


def test_memory_backend_basic_operations():
    """Test basic memory backend operations."""
    backend = MemoryBackend()

    # Test set and get
    assert backend.set("key1", "value1")
    assert backend.get("key1") == "value1"

    # Test exists
    assert backend.exists("key1")
    assert not backend.exists("key2")

    # Test delete
    assert backend.delete("key1")
    assert not backend.exists("key1")

    # Test clear
    backend.set("key2", "value2")
    backend.set("key3", "value3")
    assert backend.size() == 2
    assert backend.clear()
    assert backend.size() == 0

    backend.close()


def test_memory_backend_ttl():
    """Test TTL functionality."""
    backend = MemoryBackend()

    # Set with TTL
    backend.set("key1", "value1", ttl=0.1)  # 100ms TTL

    # Should exist immediately
    assert backend.exists("key1")

    # Wait for expiration
    import time
    time.sleep(0.15)

    # Should be expired
    assert backend.get("key1") is None
    assert not backend.exists("key1")

    backend.close()


def test_memory_backend_keys():
    """Test key listing."""
    backend = MemoryBackend()

    backend.set("key1", "value1")
    backend.set("key2", "value2")
    backend.set("key3", "value3")

    keys = list(backend.keys())
    assert len(keys) == 3
    assert "key1" in keys
    assert "key2" in keys
    assert "key3" in keys

    # Test pattern matching
    keys_pattern = list(backend.keys("key*"))
    assert len(keys_pattern) == 3

    backend.close()
