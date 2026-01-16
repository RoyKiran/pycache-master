"""Configuration management for the caching library."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union
from pathlib import Path

from pycaching.core.exceptions import CacheConfigurationError


@dataclass
class BackendConfig:
    """Configuration for a backend."""

    backend_type: str
    connection_params: Dict[str, Any] = field(default_factory=dict)
    serializer: Optional[str] = None
    max_connections: Optional[int] = None
    connection_timeout: Optional[float] = None
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class StrategyConfig:
    """Configuration for a caching strategy."""

    strategy_type: str
    strategy_params: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[float] = None  # Time to live in seconds
    max_size: Optional[int] = None  # Maximum cache size
    eviction_policy: Optional[str] = None  # LRU, LFU, FIFO


@dataclass
class CacheConfig:
    """Main configuration for cache instances."""

    backend: Union[str, BackendConfig] = "memory"
    strategy: Union[str, StrategyConfig] = "cache_aside"
    default_ttl: Optional[float] = None
    key_prefix: str = ""
    namespace: str = "default"
    enable_metrics: bool = True
    enable_logging: bool = False
    log_level: str = "INFO"
    serialization_method: str = "pickle"  # pickle, json, msgpack
    compression: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.default_ttl is not None and self.default_ttl <= 0:
            raise CacheConfigurationError("default_ttl must be positive")
        if self.serialization_method not in ("pickle", "json", "msgpack"):
            raise CacheConfigurationError(
                f"Invalid serialization_method: {self.serialization_method}"
            )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CacheConfig":
        """Create configuration from dictionary."""
        backend = config_dict.get("backend", "memory")
        if isinstance(backend, dict):
            backend = BackendConfig(**backend)

        strategy = config_dict.get("strategy", "cache_aside")
        if isinstance(strategy, dict):
            strategy = StrategyConfig(**strategy)

        return cls(
            backend=backend,
            strategy=strategy,
            default_ttl=config_dict.get("default_ttl"),
            key_prefix=config_dict.get("key_prefix", ""),
            namespace=config_dict.get("namespace", "default"),
            enable_metrics=config_dict.get("enable_metrics", True),
            enable_logging=config_dict.get("enable_logging", False),
            log_level=config_dict.get("log_level", "INFO"),
            serialization_method=config_dict.get("serialization_method", "pickle"),
            compression=config_dict.get("compression", False),
        )

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "CacheConfig":
        """Load configuration from YAML or JSON file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise CacheConfigurationError(f"Configuration file not found: {file_path}")

        import json

        if file_path.suffix in (".json",):
            with open(file_path, "r") as f:
                config_dict = json.load(f)
        elif file_path.suffix in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError:
                raise CacheConfigurationError(
                    "PyYAML is required for YAML configuration files. Install with: pip install pyyaml"
                )
            with open(file_path, "r") as f:
                config_dict = yaml.safe_load(f)
        else:
            raise CacheConfigurationError(
                f"Unsupported configuration file format: {file_path.suffix}"
            )

        return cls.from_dict(config_dict)

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Load configuration from environment variables."""
        import os

        config_dict: Dict[str, Any] = {}

        # Backend configuration
        backend_type = os.getenv("PYCACHING_BACKEND", "memory")
        config_dict["backend"] = backend_type

        # Strategy configuration
        strategy_type = os.getenv("PYCACHING_STRATEGY", "cache_aside")
        config_dict["strategy"] = strategy_type

        # Other settings
        if ttl := os.getenv("PYCACHING_TTL"):
            config_dict["default_ttl"] = float(ttl)
        if prefix := os.getenv("PYCACHING_KEY_PREFIX"):
            config_dict["key_prefix"] = prefix
        if namespace := os.getenv("PYCACHING_NAMESPACE"):
            config_dict["namespace"] = namespace
        if metrics := os.getenv("PYCACHING_METRICS"):
            config_dict["enable_metrics"] = metrics.lower() in ("true", "1", "yes")
        if logging := os.getenv("PYCACHING_LOGGING"):
            config_dict["enable_logging"] = logging.lower() in ("true", "1", "yes")
        if log_level := os.getenv("PYCACHING_LOG_LEVEL"):
            config_dict["log_level"] = log_level
        if serialization := os.getenv("PYCACHING_SERIALIZATION"):
            config_dict["serialization_method"] = serialization

        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "backend": (
                self.backend.backend_type
                if isinstance(self.backend, BackendConfig)
                else self.backend
            ),
            "strategy": (
                self.strategy.strategy_type
                if isinstance(self.strategy, StrategyConfig)
                else self.strategy
            ),
            "default_ttl": self.default_ttl,
            "key_prefix": self.key_prefix,
            "namespace": self.namespace,
            "enable_metrics": self.enable_metrics,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
            "serialization_method": self.serialization_method,
            "compression": self.compression,
        }
