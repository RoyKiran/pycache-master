"""SQLite backend implementation."""

import sqlite3
from pathlib import Path
from typing import Iterator, Optional
from threading import Lock
from datetime import datetime, timedelta

from pycaching.backends.base import BaseBackend
from pycaching.core.exceptions import BackendError
from pycaching.core.types import CacheKey, CacheValue
from pycaching.utils.serialization import PickleSerializer, Serializer


class SQLiteBackend(BaseBackend):
    """SQLite-based backend for persistent caching."""

    def __init__(
        self,
        db_path: str = "cache.db",
        serializer: Optional[Serializer] = None,
        name: str = "sqlite",
        enable_metadata: bool = True,
    ):
        super().__init__(name, enable_metadata)
        self.db_path = Path(db_path)
        self.serializer = serializer or PickleSerializer()
        self._lock = Lock()
        self._connection: Optional[sqlite3.Connection] = None

        # Initialize database
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=5.0,
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _init_db(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        with self._lock:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
            """)
            conn.commit()

    def _get_impl(self, key: CacheKey) -> Optional[CacheValue]:
        """Get a value from SQLite."""
        key_str = str(key)
        conn = self._get_connection()

        try:
            with self._lock:
                cursor = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?",
                    (key_str,),
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                # Check expiration
                expires_at = row["expires_at"]
                if expires_at:
                    expires_dt = datetime.fromisoformat(expires_at)
                    if datetime.now() >= expires_dt:
                        # Expired, delete and return None
                        conn.execute("DELETE FROM cache WHERE key = ?", (key_str,))
                        conn.commit()
                        return None

                # Deserialize value
                value_data = row["value"]
                value = self.serializer.deserialize(value_data)
                return value
        except Exception as e:
            raise BackendError(f"Failed to get value from SQLite: {e}") from e

    def _set_impl(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value in SQLite."""
        key_str = str(key)
        conn = self._get_connection()

        try:
            with self._lock:
                # Serialize value
                value_data = self.serializer.serialize(value)

                # Calculate expiration
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.now() + timedelta(seconds=ttl)

                # Insert or update
                conn.execute("""
                    INSERT OR REPLACE INTO cache (key, value, expires_at)
                    VALUES (?, ?, ?)
                """, (key_str, value_data, expires_at.isoformat() if expires_at else None))
                conn.commit()
                return True
        except Exception as e:
            raise BackendError(f"Failed to set value in SQLite: {e}") from e

    def _delete_impl(self, key: CacheKey) -> bool:
        """Delete a value from SQLite."""
        key_str = str(key)
        conn = self._get_connection()

        try:
            with self._lock:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key_str,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise BackendError(f"Failed to delete value from SQLite: {e}") from e

    def _exists_impl(self, key: CacheKey) -> bool:
        """Check if a key exists in SQLite."""
        key_str = str(key)
        conn = self._get_connection()

        try:
            with self._lock:
                cursor = conn.execute(
                    "SELECT 1 FROM cache WHERE key = ?",
                    (key_str,),
                )
                return cursor.fetchone() is not None
        except Exception as e:
            raise BackendError(f"Failed to check existence in SQLite: {e}") from e

    def _clear_impl(self) -> bool:
        """Clear all entries from SQLite."""
        conn = self._get_connection()

        try:
            with self._lock:
                conn.execute("DELETE FROM cache")
                conn.commit()
                return True
        except Exception as e:
            raise BackendError(f"Failed to clear SQLite cache: {e}") from e

    def keys(self, pattern: Optional[str] = None) -> Iterator[CacheKey]:
        """Get all keys from SQLite."""
        conn = self._get_connection()

        try:
            with self._lock:
                if pattern is None:
                    cursor = conn.execute("SELECT key FROM cache")
                else:
                    # SQLite LIKE pattern matching
                    cursor = conn.execute("SELECT key FROM cache WHERE key LIKE ?", (pattern,))

                for row in cursor:
                    yield row["key"]
        except Exception as e:
            raise BackendError(f"Failed to get keys from SQLite: {e}") from e

    def size(self) -> int:
        """Get the number of entries in SQLite."""
        conn = self._get_connection()

        try:
            with self._lock:
                cursor = conn.execute("SELECT COUNT(*) as count FROM cache")
                row = cursor.fetchone()
                return row["count"] if row else 0
        except Exception as e:
            raise BackendError(f"Failed to get size from SQLite: {e}") from e

    def close(self) -> None:
        """Close the database connection."""
        super().close()
        if self._connection is not None:
            with self._lock:
                self._connection.close()
                self._connection = None
