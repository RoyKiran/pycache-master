"""Refresh-ahead strategy implementation."""

from typing import Callable, Dict, Optional
from threading import Lock, Thread
import time

from pycaching.core.backend import Backend
from pycaching.strategies.base import BaseStrategy
from pycaching.core.types import CacheKey, CacheValue


RefreshCallback = Callable[[CacheKey], CacheValue]


class RefreshAheadStrategy(BaseStrategy):
    """
    Refresh-ahead strategy.

    Entries are refreshed proactively before they expire, reducing
    the chance of cache misses.
    """

    def __init__(
        self,
        refresh_callback: Optional[RefreshCallback] = None,
        refresh_threshold: float = 0.8,  # Refresh when 80% of TTL has passed
        name: str = "refresh_ahead",
    ):
        super().__init__(name)
        self.refresh_callback = refresh_callback
        self.refresh_threshold = refresh_threshold
        self._refresh_times: Dict[CacheKey, float] = {}
        self._lock = Lock()
        self._running = False
        self._refresh_thread: Optional[Thread] = None

    def get(
        self,
        backend: Backend,
        key: CacheKey,
        miss_callback: Optional[CacheMissCallback] = None,
    ) -> Optional[CacheValue]:
        """Get a value, scheduling refresh if needed."""
        value = backend.get(key)

        # If found, check if refresh is needed
        if value is not None and self.refresh_callback is not None:
            self._schedule_refresh(backend, key)

        # If miss, use callback
        if value is None and miss_callback is not None:
            value = miss_callback(key)
            if value is not None:
                backend.set(key, value)
                with self._lock:
                    self._refresh_times[key] = time.time()

        return value

    def set(
        self,
        backend: Backend,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[float] = None,
    ) -> bool:
        """Set a value and record refresh time."""
        result = backend.set(key, value, ttl)
        if result:
            with self._lock:
                self._refresh_times[key] = time.time()
        return result

    def _schedule_refresh(self, backend: Backend, key: CacheKey) -> None:
        """Schedule a refresh for a key if needed."""
        if self.refresh_callback is None:
            return

        with self._lock:
            last_refresh = self._refresh_times.get(key, 0)
            current_time = time.time()
            time_since_refresh = current_time - last_refresh

            # Simple heuristic: refresh if enough time has passed
            # In a real implementation, you'd check TTL metadata
            if time_since_refresh > 1.0:  # Refresh if more than 1 second passed
                # Schedule async refresh
                if not self._running:
                    self._start_refresh_thread(backend)

    def _start_refresh_thread(self, backend: Backend) -> None:
        """Start the background refresh thread."""
        if self._running:
            return

        self._running = True

        def refresh_worker():
            while self._running:
                try:
                    time.sleep(0.5)  # Check every 0.5 seconds
                    self._refresh_expiring_keys(backend)
                except Exception:
                    pass  # Ignore errors in background thread

        self._refresh_thread = Thread(target=refresh_worker, daemon=True)
        self._refresh_thread.start()

    def _refresh_expiring_keys(self, backend: Backend) -> None:
        """Refresh keys that are about to expire."""
        if self.refresh_callback is None:
            return

        with self._lock:
            keys_to_refresh = list(self._refresh_times.keys())

        for key in keys_to_refresh:
            try:
                if backend.exists(key):
                    # Refresh the value
                    new_value = self.refresh_callback(key)
                    if new_value is not None:
                        backend.set(key, new_value)
                        with self._lock:
                            self._refresh_times[key] = time.time()
            except Exception:
                pass  # Ignore errors for individual keys

    def delete(self, backend: Backend, key: CacheKey) -> bool:
        """Delete a key and remove refresh tracking."""
        result = backend.delete(key)
        if result:
            with self._lock:
                self._refresh_times.pop(key, None)
        return result

    def clear(self, backend: Backend) -> bool:
        """Clear cache and stop refresh thread."""
        self._stop_refresh_thread()
        with self._lock:
            self._refresh_times.clear()
        return backend.clear()

    def _stop_refresh_thread(self) -> None:
        """Stop the background refresh thread."""
        self._running = False
        if self._refresh_thread is not None:
            self._refresh_thread.join(timeout=1.0)
