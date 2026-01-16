"""Factory functions for easy cache instantiation."""

from typing import Optional, Union

from pycaching.backends.async_wrapper import AsyncBackendWrapper
from pycaching.backends.file_backend import FileBackend
from pycaching.backends.memory import MemoryBackend
from pycaching.backends.redis_backend import RedisBackend
from pycaching.backends.sqlite_backend import SQLiteBackend
from pycaching.core.backend import Backend
from pycaching.core.cache import CacheManager
from pycaching.core.config import CacheConfig
from pycaching.core.strategy import Strategy
from pycaching.strategies.cache_aside import CacheAsideStrategy
from pycaching.strategies.read_through import ReadThroughStrategy
from pycaching.strategies.refresh_ahead import RefreshAheadStrategy
from pycaching.strategies.ttl import TTLStrategy
from pycaching.strategies.write_back import WriteBackStrategy
from pycaching.strategies.write_through import WriteThroughStrategy


def create_backend(
    backend_type: str = "memory",
    **kwargs,
) -> Backend:
    """
    Create a backend instance.

    Args:
        backend_type: Type of backend ('memory', 'redis', 'file', 'sqlite', etc.)
        **kwargs: Backend-specific configuration

    Returns:
        Backend instance
    """
    backend_type = backend_type.lower()

    if backend_type == "memory":
        return MemoryBackend(**kwargs)
    elif backend_type == "file":
        return FileBackend(**kwargs)
    elif backend_type == "sqlite":
        return SQLiteBackend(**kwargs)
    elif backend_type == "redis":
        return RedisBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def create_strategy(
    strategy_type: str = "cache_aside",
    **kwargs,
) -> Strategy:
    """
    Create a strategy instance.

    Args:
        strategy_type: Type of strategy
        **kwargs: Strategy-specific configuration

    Returns:
        Strategy instance
    """
    strategy_type = strategy_type.lower()

    if strategy_type == "cache_aside":
        return CacheAsideStrategy(**kwargs)
    elif strategy_type == "write_through":
        return WriteThroughStrategy(**kwargs)
    elif strategy_type == "write_back":
        return WriteBackStrategy(**kwargs)
    elif strategy_type == "read_through":
        return ReadThroughStrategy(**kwargs)
    elif strategy_type == "refresh_ahead":
        return RefreshAheadStrategy(**kwargs)
    elif strategy_type == "ttl":
        return TTLStrategy(**kwargs)
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")


def create_cache(
    backend: Union[str, Backend] = "memory",
    strategy: Union[str, Strategy] = "cache_aside",
    config: Optional[CacheConfig] = None,
    **kwargs,
) -> CacheManager:
    """
    Create a cache manager instance.

    Args:
        backend: Backend name or instance
        strategy: Strategy name or instance
        config: Optional CacheConfig
        **kwargs: Additional configuration

    Returns:
        CacheManager instance
    """
    # Create backend if string
    if isinstance(backend, str):
        backend = create_backend(backend, **kwargs)

    # Create strategy if string
    if isinstance(strategy, str):
        strategy = create_strategy(strategy, **kwargs)

    # Use provided config or create default
    if config is None:
        config = CacheConfig()

    return CacheManager(backend=backend, strategy=strategy, config=config)


def create_async_cache(
    backend: Union[str, Backend] = "memory",
    strategy: Union[str, Strategy] = "cache_aside",
    config: Optional[CacheConfig] = None,
    **kwargs,
):
    """
    Create an async cache manager instance.

    Args:
        backend: Backend name or instance
        strategy: Strategy name or instance
        config: Optional CacheConfig
        **kwargs: Additional configuration

    Returns:
        AsyncCacheManager instance
    """
    from pycaching.backends.async_wrapper import AsyncBackendWrapper
    from pycaching.core.async_cache import AsyncCacheManager
    from pycaching.strategies.async_wrapper import AsyncStrategyWrapper

    # Create backend if string
    if isinstance(backend, str):
        backend = create_backend(backend, **kwargs)

    # Wrap backend if not async
    if not hasattr(backend, "__aenter__"):
        backend = AsyncBackendWrapper(backend)

    # Create strategy if string
    if isinstance(strategy, str):
        strategy = create_strategy(strategy, **kwargs)

    # Wrap strategy if not async
    if not hasattr(strategy, "__aenter__"):
        strategy = AsyncStrategyWrapper(strategy)

    # Use provided config or create default
    if config is None:
        config = CacheConfig()

    return AsyncCacheManager(backend=backend, strategy=strategy, config=config)
