"""Unit tests for cache manager."""

import pytest

from pycaching.backends.memory import MemoryBackend
from pycaching.core.cache import CacheManager
from pycaching.core.config import CacheConfig
from pycaching.strategies.cache_aside import CacheAsideStrategy


def test_cache_manager_basic():
    """Test basic cache manager operations."""
    backend = MemoryBackend()
    strategy = CacheAsideStrategy()
    config = CacheConfig()
    manager = CacheManager(backend, strategy, config)

    # Test set and get
    assert manager.set("key1", "value1")
    assert manager.get("key1") == "value1"

    # Test dictionary-style access
    manager["key2"] = "value2"
    assert manager["key2"] == "value2"
    assert "key2" in manager
    assert len(manager) == 2

    # Test delete
    del manager["key1"]
    assert "key1" not in manager

    manager.close()


def test_cache_manager_with_namespace():
    """Test cache manager with namespace."""
    backend = MemoryBackend()
    strategy = CacheAsideStrategy()
    config = CacheConfig(namespace="test", key_prefix="app")
    manager = CacheManager(backend, strategy, config)

    manager.set("key1", "value1")
    # Key should be prefixed
    keys = list(backend.keys())
    assert any("test:app:key1" in str(k) for k in keys)

    manager.close()
