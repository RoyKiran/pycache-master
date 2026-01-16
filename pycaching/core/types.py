"""Type definitions and protocols for the caching library."""

from typing import Any, Callable, Dict, Optional, Protocol, Union
from datetime import datetime, timedelta

# Type aliases
CacheKey = Union[str, bytes, int, float]
CacheValue = Any
CacheEntry = Dict[str, Any]


class Serializer(Protocol):
    """Protocol for serialization/deserialization."""

    def serialize(self, value: CacheValue) -> bytes:
        """Serialize a value to bytes."""
        ...

    def deserialize(self, data: bytes) -> CacheValue:
        """Deserialize bytes to a value."""
        ...


class KeyGenerator(Protocol):
    """Protocol for key generation."""

    def generate(self, *args: Any, **kwargs: Any) -> CacheKey:
        """Generate a cache key from arguments."""
        ...


# Cache metadata
class CacheMetadata:
    """Metadata associated with a cache entry."""

    def __init__(
        self,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
    ):
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.access_count = access_count
        self.last_accessed = last_accessed or self.created_at
        self.tags = tags or []

    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at

    def update_access(self) -> None:
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheMetadata":
        """Create metadata from dictionary."""
        return cls(
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            tags=data.get("tags", []),
        )


# Callback types
CacheMissCallback = Callable[[CacheKey], CacheValue]
CacheHitCallback = Callable[[CacheKey, CacheValue], None]
CacheSetCallback = Callable[[CacheKey, CacheValue], None]
CacheDeleteCallback = Callable[[CacheKey], None]
