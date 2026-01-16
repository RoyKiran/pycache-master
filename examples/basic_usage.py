"""Basic usage examples for pycaching."""

from pycaching import create_cache
from pycaching.api.decorator import cache
from pycaching.api.context import CacheContext


def example_basic_cache():
    """Basic cache usage."""
    cache = create_cache(backend="memory", strategy="cache_aside")

    # Set and get
    cache.set("key1", "value1")
    value = cache.get("key1")
    print(f"Value: {value}")

    # With TTL
    cache.set("key2", "value2", ttl=60)  # 60 seconds

    # Delete
    cache.delete("key1")

    # Clear all
    cache.clear()

    cache.close()


def example_decorator():
    """Using the decorator API."""
    @cache(ttl=3600)
    def expensive_function(x):
        return x * 2

    result = expensive_function(5)
    print(f"Result: {result}")


def example_context_manager():
    """Using the context manager API."""
    def compute_value(key):
        return f"computed_{key}"

    with CacheContext("my_key") as ctx:
        value = ctx.get_or_compute(compute_value)
        print(f"Value: {value}")


def example_redis():
    """Using Redis backend."""
    cache = create_cache(
        backend="redis",
        host="localhost",
        port=6379,
    )

    cache.set("key1", "value1")
    value = cache.get("key1")
    print(f"Value: {value}")

    cache.close()


if __name__ == "__main__":
    example_basic_cache()
    example_decorator()
    example_context_manager()
    example_redis()
