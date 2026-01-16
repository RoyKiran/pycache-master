"""Custom exceptions for the caching library."""


class CacheError(Exception):
    """Base exception for all cache-related errors."""

    pass


class BackendError(CacheError):
    """Exception raised when a backend operation fails."""

    pass


class StrategyError(CacheError):
    """Exception raised when a strategy operation fails."""

    pass


class CacheKeyError(CacheError, KeyError):
    """Exception raised when a cache key is not found or invalid."""

    pass


class CacheSerializationError(CacheError):
    """Exception raised when serialization/deserialization fails."""

    pass


class CacheTimeoutError(CacheError):
    """Exception raised when a cache operation times out."""

    pass


class CacheConfigurationError(CacheError):
    """Exception raised when cache configuration is invalid."""

    pass
