"""Write-back (write-behind) strategy implementation."""

from typing import Callable, Dict, Optional
from threading import Lock
import time

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue


WriteCallback = Callable[[CacheKey, CacheValue], None]


class WriteBackStrategy(BaseStrategy):
    """
    Write-back (write-behind) strategy.

    Data is written to the cache immediately, and written to the underlying
    data store asynchronously or in batches.
    """

    def __init__(
        self,
        write_callback: Optional[WriteCallback] = None,
        batch_size: int = 10,
        flush_interval: float = 5.0,
        name: str = "write_back",
    ):
        super().__init__(name)
        self.write_callback = write_callback
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._write_queue: Dict[CacheKey, CacheValue] = {}
        self._lock = Lock()
        self._last_flush = time.time()

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value, writing to cache immediately and queueing for data store."""
        # Write to cache immediately
        result = backend.set(key, value, ttl)

        # Queue for write to data store
        if self.write_callback is not None and result:
            with self._lock:
                self._write_queue[key] = value
                self._maybe_flush()

        return result

    def _maybe_flush(self) -> None:
        """Flush write queue if conditions are met."""
        current_time = time.time()
        should_flush = (
            len(self._write_queue) >= self.batch_size
            or (current_time - self._last_flush) >= self.flush_interval
        )

        if should_flush and self.write_callback:
            self._flush()

    def _flush(self) -> None:
        """Flush all queued writes to the data store."""
        if not self._write_queue:
            return

        queue_copy = self._write_queue.copy()
        self._write_queue.clear()
        self._last_flush = time.time()

        # Write all queued items
        for key, value in queue_copy.items():
            try:
                self.write_callback(key, value)
            except Exception:
                # On error, re-queue the item
                self._write_queue[key] = value

    def flush(self) -> None:
        """Manually flush the write queue."""
        with self._lock:
            self._flush()

    def clear(self, backend: Backend) -> bool:
        """Clear cache and flush any pending writes."""
        with self._lock:
            self._flush()
        return backend.clear()
